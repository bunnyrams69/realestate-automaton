"""
Automated Multi-Touch Lead Nurturing Service
Executes cadenced 24h, 72h, and 7-day follow-ups via WhatsApp and OpenRouter
with atomic worker locking (SKIP LOCKED), crash recovery, and retry management.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.settings import settings
from app.core.constants import (
    FollowUpStatus,
    MessageDirection,
    MessageProcessingStatus,
    MessageType,
)
from app.core.logging import logger
from app.integrations.openrouter.client import openrouter_client
from app.integrations.whatsapp.client import whatsapp_client
from app.models.follow_up import FollowUpTask
from app.models.message import Message
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.follow_up_repository import FollowUpRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.property_repository import PropertyRepository


CADENCE_HOURS = {
    1: 24,    # Attempt 1: 24 hours later
    2: 72,    # Attempt 2: 72 hours later (3 days)
    3: 168,   # Attempt 3: 7 days later
    4: 336,   # Attempt 4: 14 days later
}


class FollowUpService:
    """Service orchestrating cadenced lead re-engagement tasks with concurrency safety."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.task_repo = FollowUpRepository(session)
        self.lead_repo = LeadRepository(session)
        self.conversation_repo = ConversationRepository(session)
        self.message_repo = MessageRepository(session)
        self.property_repo = PropertyRepository(session)

    async def schedule_next_follow_up(
        self,
        lead_id: uuid.UUID,
        attempt: int = 1,
        custom_delay_hours: Optional[int] = None,
    ) -> Optional[FollowUpTask]:
        """Schedule a nurturing task for a lead."""
        if attempt > settings.MAX_FOLLOW_UP_ATTEMPTS:
            logger.info(f"Lead {lead_id} reached max follow-up attempts ({settings.MAX_FOLLOW_UP_ATTEMPTS}).")
            return None

        delay = custom_delay_hours if custom_delay_hours is not None else CADENCE_HOURS.get(attempt, 24)
        run_at = datetime.now(timezone.utc) + timedelta(hours=delay)

        task = FollowUpTask(
            lead_id=lead_id,
            scheduled_for=run_at,
            attempt_number=attempt,
            status=FollowUpStatus.PENDING.value,
            task_type="nurturing_message",
            payload_json={"cadence_stage": attempt},
        )
        saved = await self.task_repo.create(task)
        logger.info(f"Scheduled follow-up attempt {attempt} for lead {lead_id} at {run_at.isoformat()}")
        return saved

    async def execute_due_tasks(self, limit: int = 25) -> int:
        """
        Poll and execute all currently due follow-up tasks:
        1. Recover stale tasks from crashed worker processes
        2. Atomically claim due tasks with FOR UPDATE SKIP LOCKED
        3. Suppress if lead opted out or under human takeover
        4. Generate contextual re-engagement message
        5. Dispatch via WhatsApp
        6. Schedule next cadence step
        """
        # 1. Recover any tasks abandoned by killed workers
        recovered = await self.task_repo.recover_stale_tasks(stale_timeout_minutes=10)
        if recovered > 0:
            logger.warning(f"Recovered {recovered} stale follow-up tasks from crashed processes.")

        # 2. Atomically claim due tasks (prevents multi-worker duplicate runs)
        due_tasks = await self.task_repo.claim_due_tasks(limit=limit)
        executed_count = 0

        for task in due_tasks:
            lead = await self.lead_repo.get_by_id(task.lead_id)
            if not lead:
                await self.task_repo.mark_failed(task, "Associated lead not found")
                continue

            # 3. Opt-out check
            if lead.consent_status == "OPTED_OUT":
                logger.info(f"Cancelling follow-up for opted-out lead: {lead.id}")
                task.status = FollowUpStatus.CANCELLED.value
                await self.task_repo.cancel_pending_for_lead(lead.id)
                continue

            # 4. Human takeover check
            active_conv = await self.conversation_repo.get_active_for_lead(lead.id)
            if active_conv and active_conv.is_human_takeover:
                logger.info(f"Cancelling automated follow-up for human-managed lead: {lead.id}")
                task.status = FollowUpStatus.CANCELLED.value
                await self.task_repo.cancel_pending_for_lead(lead.id)
                continue

            # 5. Generate empathetic message with AI or fallback
            prompt = self._build_nurturing_prompt(lead, task.attempt_number)
            try:
                message_text = await openrouter_client.generate_response(
                    messages=[
                        {"role": "system", "content": "You are Aura, friendly real estate advisor. Keep WhatsApp follow-up under 3 sentences."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                )
            except Exception as e:
                logger.warning(f"Failed to generate LLM follow-up text for lead {lead.id}: {e}")
                message_text = (
                    f"Hi {lead.name or 'there'}! Just checking in to see if you had any questions "
                    f"about properties in {lead.preferred_location or 'Bangalore'}. "
                    f"We have exciting new units available—let me know if you'd like a brochure!"
                )

            # 6. Dispatch via WhatsApp
            try:
                await whatsapp_client.send_text_message(to=lead.phone, text=message_text)

                if active_conv:
                    outbound_msg = Message(
                        conversation_id=active_conv.id,
                        direction=MessageDirection.OUTBOUND.value,
                        message_type=MessageType.TEXT.value,
                        content=message_text,
                        status=MessageProcessingStatus.SENT.value,
                        metadata_json={"automated_follow_up": True, "attempt": task.attempt_number},
                    )
                    await self.message_repo.create(outbound_msg)

                await self.task_repo.mark_executed(task)
                executed_count += 1

                # 7. Schedule next touchpoint
                next_attempt = task.attempt_number + 1
                if next_attempt <= settings.MAX_FOLLOW_UP_ATTEMPTS:
                    await self.schedule_next_follow_up(lead.id, attempt=next_attempt)

            except Exception as e:
                logger.error(f"Failed to deliver follow-up WhatsApp message to {lead.phone}: {e}")
                await self.task_repo.mark_failed(task, str(e))

        return executed_count

    def _build_nurturing_prompt(self, lead, attempt: int) -> str:
        """Compose context-specific nurturing prompt based on cadence tier."""
        loc = lead.preferred_location or "the city"
        p_type = lead.property_type or "homes"
        budget = f"around INR {lead.budget_max:,}" if lead.budget_max else "your budget"

        if attempt == 1:
            return (
                f"Write a friendly 24-hour follow-up WhatsApp message to {lead.name or 'a prospective buyer'}. "
                f"They were exploring {p_type} in {loc} ({budget}). "
                f"Ask if they had a chance to review the details and offer to share video walkthroughs or floor plans."
            )
        elif attempt == 2:
            return (
                f"Write a 72-hour follow-up WhatsApp message to {lead.name or 'a prospective buyer'}. "
                f"Mention that our team just received fresh inventory for {p_type} in {loc}. "
                f"Ask if they would like to view top-rated options this weekend."
            )
        else:
            return (
                f"Write a gentle, zero-pressure 7-day re-engagement WhatsApp message to {lead.name or 'a prospective buyer'}. "
                f"Ask if their timeline for {loc} has shifted or if they need any market updates."
            )
