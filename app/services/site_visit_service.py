"""
Site Visit Management & Scheduling Service
Coordinates appointment bookings, interval conflict checking, calendar generation,
lead qualification updates, and WhatsApp notifications.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.settings import settings
from app.core.constants import LeadCategory, SiteVisitStatus
from app.core.exceptions import EntityNotFoundException, ValidationException
from app.core.logging import logger
from app.integrations.calendar.calendar_service import calendar_service
from app.integrations.whatsapp.client import whatsapp_client
from app.models.site_visit import SiteVisit
from app.repositories.follow_up_repository import FollowUpRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.property_repository import PropertyRepository
from app.repositories.site_visit_repository import SiteVisitRepository
from app.schemas.site_visit import SiteVisitCreate, SiteVisitResponse, SiteVisitUpdate
from app.services.lead_service import LeadService


class SiteVisitService:
    """Service handling site visit lifecycle and calendar coordination."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SiteVisitRepository(session)
        self.lead_repo = LeadRepository(session)
        self.property_repo = PropertyRepository(session)
        self.follow_up_repo = FollowUpRepository(session)
        self.lead_service = LeadService(session)

    async def schedule_visit(self, payload: SiteVisitCreate) -> SiteVisitResponse:
        """
        Book a new on-site property walkthrough:
        1. Validate lead & property existence
        2. Detect conflicting bookings using interval overlap
        3. Persist site visit appointment
        4. Cancel pending automated follow-ups
        5. Update lead qualification (engagement bonus without corrupting stated timeline)
        6. Generate calendar links and notify via WhatsApp
        """
        # 1. Validate entities
        lead = await self.lead_repo.get_by_id(payload.lead_id)
        if not lead:
            raise EntityNotFoundException(f"Lead '{payload.lead_id}' not found")

        prop = await self.property_repo.get_by_id(payload.property_id)
        if not prop:
            raise EntityNotFoundException(f"Property '{payload.property_id}' not found")

        # 2. Check true interval conflict
        has_conflict = await self.repo.check_interval_conflict(
            scheduled_time=payload.scheduled_time,
            duration_minutes=payload.duration_minutes,
            property_id=payload.property_id,
            agent_id=payload.assigned_agent_id,
        )
        if has_conflict:
            raise ValidationException("An appointment is already scheduled that overlaps with this time slot.")

        # 3. Create site visit record
        visit = SiteVisit(
            lead_id=payload.lead_id,
            property_id=payload.property_id,
            assigned_agent_id=payload.assigned_agent_id,
            scheduled_time=payload.scheduled_time,
            duration_minutes=payload.duration_minutes,
            status=payload.status.value if payload.status else SiteVisitStatus.REQUESTED.value,
            notes=payload.notes,
        )
        saved = await self.repo.create(visit)

        # 4. Cancel pending automated follow-up messages since lead has actively booked
        await self.follow_up_repo.cancel_pending_for_lead(lead.id)

        # 5. Update lead qualification with site visit engagement bonus (preserve genuine customer timeline)
        await self.lead_service.calculate_and_update_qualification(lead, has_active_site_visit=True)

        # 6. Generate Calendar Event & Links
        title = f"Site Visit: {prop.name} with Prestige Realty"
        desc = (
            f"Scheduled site walkthrough for {prop.name} ({prop.property_type}).\n"
            f"Location: {prop.location}\n"
            f"Address: {prop.address}\n"
            f"Lead: {lead.name or 'Valued Prospect'} ({lead.phone})"
        )
        cal_link = calendar_service.generate_google_calendar_link(
            title=title,
            start_time=payload.scheduled_time,
            duration_minutes=payload.duration_minutes,
            description=desc,
            location=prop.address or prop.location,
        )

        # 7. Dispatch WhatsApp Confirmation
        time_str = payload.scheduled_time.strftime("%A, %d %B %Y at %I:%M %p")
        confirmation_msg = (
            f"🎉 *Site Visit Confirmed!*\n\n"
            f"📍 *Property:* {prop.name}\n"
            f"🗓 *Date & Time:* {time_str}\n"
            f"🏢 *Address:* {prop.address or prop.location}\n\n"
            f"📅 *Add to Google Calendar:* {cal_link}\n\n"
            f"Our property specialist will welcome you at the location. "
            f"Reply to this chat if you need to reschedule or need directions!"
        )
        try:
            await whatsapp_client.send_text_message(to=lead.phone, text=confirmation_msg)
        except Exception as e:
            logger.warning(f"Could not dispatch site visit WhatsApp confirmation: {e}")

        return SiteVisitResponse.model_validate(saved)

    async def reschedule_visit(
        self,
        visit_id: uuid.UUID,
        new_time: datetime,
        duration_minutes: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> SiteVisitResponse:
        """Reschedule an existing site visit with interval conflict checking."""
        visit = await self.repo.get_by_id(visit_id)
        if not visit:
            raise EntityNotFoundException(f"Site visit '{visit_id}' not found")

        duration = duration_minutes or visit.duration_minutes

        # Check conflict excluding current appointment
        has_conflict = await self.repo.check_interval_conflict(
            scheduled_time=new_time,
            duration_minutes=duration,
            property_id=visit.property_id,
            agent_id=visit.assigned_agent_id,
            exclude_visit_id=visit_id,
        )
        if has_conflict:
            raise ValidationException("The requested rescheduled time slot conflicts with an existing booking.")

        visit.scheduled_time = new_time
        visit.duration_minutes = duration
        visit.status = SiteVisitStatus.RESCHEDULED.value
        if notes:
            visit.notes = f"{visit.notes or ''}\nRescheduled: {notes}".strip()

        await self.session.flush()
        await self.session.refresh(visit)

        # Notify lead of updated schedule
        lead = await self.lead_repo.get_by_id(visit.lead_id)
        prop = await self.property_repo.get_by_id(visit.property_id)
        if lead and prop:
            time_str = new_time.strftime("%A, %d %B %Y at %I:%M %p")
            msg = f"🗓 *Site Visit Rescheduled*\n\nYour walkthrough for *{prop.name}* is now set for *{time_str}*."
            try:
                await whatsapp_client.send_text_message(to=lead.phone, text=msg)
            except Exception as e:
                logger.warning(f"Failed to send reschedule notification: {e}")

        return SiteVisitResponse.model_validate(visit)

    async def cancel_visit(
        self,
        visit_id: uuid.UUID,
        reason: Optional[str] = None,
    ) -> SiteVisitResponse:
        """Cancel a site visit and recalculate lead score."""
        visit = await self.repo.get_by_id(visit_id)
        if not visit:
            raise EntityNotFoundException(f"Site visit '{visit_id}' not found")

        visit.status = SiteVisitStatus.CANCELLED.value
        if reason:
            visit.notes = f"{visit.notes or ''}\nCancelled: {reason}".strip()

        await self.session.flush()
        await self.session.refresh(visit)

        # Recalculate lead qualification (re-evaluates active visits)
        lead = await self.lead_repo.get_by_id(visit.lead_id)
        if lead:
            await self.lead_service.calculate_and_update_qualification(lead)

            prop = await self.property_repo.get_by_id(visit.property_id)
            prop_name = prop.name if prop else "property"
            msg = f"Your site visit appointment for *{prop_name}* has been cancelled. Let us know when you would like to reschedule!"
            try:
                await whatsapp_client.send_text_message(to=lead.phone, text=msg)
            except Exception as e:
                logger.warning(f"Failed to send cancellation notification: {e}")

        return SiteVisitResponse.model_validate(visit)

    async def get_visit_by_id(self, visit_id: uuid.UUID) -> SiteVisitResponse:
        """Fetch visit by ID or raise 404."""
        visit = await self.repo.get_by_id(visit_id)
        if not visit:
            raise EntityNotFoundException(f"Site visit '{visit_id}' not found")
        return SiteVisitResponse.model_validate(visit)

    async def list_visits_for_lead(self, lead_id: uuid.UUID) -> List[SiteVisitResponse]:
        """Fetch all site visits for a lead."""
        visits = await self.repo.get_by_lead(lead_id)
        return [SiteVisitResponse.model_validate(v) for v in visits]

    async def update_status(
        self,
        visit_id: uuid.UUID,
        new_status: SiteVisitStatus,
        notes: Optional[str] = None,
    ) -> SiteVisitResponse:
        """Update appointment lifecycle state (CONFIRMED, COMPLETED, CANCELLED)."""
        visit = await self.repo.get_by_id(visit_id)
        if not visit:
            raise EntityNotFoundException(f"Site visit '{visit_id}' not found")

        visit.status = new_status.value
        if notes:
            visit.notes = f"{visit.notes or ''}\n{notes}".strip()

        await self.session.flush()
        await self.session.refresh(visit)

        # If cancelled or completed, recalculate lead qualification
        lead = await self.lead_repo.get_by_id(visit.lead_id)
        if lead:
            await self.lead_service.calculate_and_update_qualification(lead)

        return SiteVisitResponse.model_validate(visit)
