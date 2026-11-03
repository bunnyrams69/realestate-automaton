"""
AI Sales Agent State Machine & Orchestrator
Coordinates inbound WhatsApp messages, OpenRouter reasoning, lead qualification,
property matching, and autonomous conversational actions.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.settings import settings
from app.core.constants import (
    ConversationState,
    LeadCategory,
    MessageDirection,
    MessageProcessingStatus,
    MessageType,
    PropertyType,
)
from app.core.logging import logger
from app.integrations.openrouter.client import openrouter_client
from app.integrations.whatsapp.client import whatsapp_client
from app.models.conversation import Conversation
from app.models.lead import Lead
from app.models.message import Message
from app.repositories.ai_decision_repository import AIDecisionRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.follow_up_repository import FollowUpRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.property_repository import PropertyRepository
from app.services.image_library_service import image_library_service
from app.services.lead_service import LeadService
from app.services.property_service import PropertyService
from app.services.whatsapp_service import ParsedIncomingMessage
from app.agents.sales_agent_v2 import SalesAgentV2, AppDeps


CAL_BOOKING_LINK = settings.CAL_COM_BOOKING_URL or "https://cal.com/gunda-ganesh-ofduvx/site-visit"

SALES_ASSISTANT_SYSTEM_PROMPT = f"""SYSTEM PROMPT: PRESTIGE REALTY HYDERABAD – AI REAL ESTATE SALES AGENT

1. YOUR IDENTITY & HYDERABAD LOCAL EXPERTISE
You are the official Senior AI Real Estate Sales Consultant for Prestige Realty Hyderabad.
Your responsibility is to interact with customers through WhatsApp, understand their property requirements, qualify their buying intent, recommend suitable properties in West Hyderabad (Kokapet, Financial District, Gachibowli, Kondapur, Nanakramguda, Tellapur), answer questions, handle objections, and convert genuine buyers into confirmed property site visits.
You speak with deep knowledge of Hyderabad real estate: 100% Vastu compliance (East/West facing), Outer Ring Road (ORR) connectivity, HMDA and TG-RERA approvals, and luxury gated amenities.
Never pretend to be human. Be warm, professional, and knowledgeable.

2. MANDATORY WORKFLOW RULES
Rule 1: INSTANT IMAGES UPON LOCATION + PROPERTY TYPE CONFIRMATION (CRITICAL)
As soon as the customer confirms their preferred location and property type (Villa, Apartment, or Plot):
- Immediately present matching properties and dispatch preview images/photos directly to their WhatsApp.
- Reference the sent photos in your reply and ask about budget or BHK.
- Never make the buyer complete a long questionnaire before seeing visual proof.

Rule 2: Ask only ONE question at a time.
Rule 3: Keep WhatsApp messages short (1 to 2 short sentences, under 50 words).
Rule 4: Quote prices strictly in Indian format (₹ Lakhs, ₹ Crores).
Rule 5: Schedule site visits directly in chat using available slots.
"""
"""


class SalesAgent:
    """Autonomous Real Estate Sales Conversational Agent."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.lead_repo = LeadRepository(session)
        self.conversation_repo = ConversationRepository(session)
        self.message_repo = MessageRepository(session)
        self.property_repo = PropertyRepository(session)
        self.ai_decision_repo = AIDecisionRepository(session)
        self.lead_service = LeadService(session)
        self.property_service = PropertyService(session)
        self.agent_v2 = SalesAgentV2(llm=openrouter_client, deps=AppDeps(session))

    async def process_incoming_message(self, msg: ParsedIncomingMessage) -> Dict[str, Any]:
        """
        Orchestrate end-to-end processing of an incoming WhatsApp message:
        1. Lead & conversation resolution
        2. Human handoff check
        3. Intent & opt-out evaluation
        4. Structured preference extraction & qualification recalculation
        5. Real-time property matching
        6. Conversational reply generation via OpenRouter
        7. Outbound WhatsApp dispatch & state persistence
        """
        masked_phone = f"{msg.sender_phone[:4]}****{msg.sender_phone[-4:]}" if len(msg.sender_phone) >= 8 else "****"
        logger.info(f"Processing inbound message from {masked_phone}: '{msg.content}'")

        # 1. Resolve or create lead
        lead = await self.lead_service.get_or_create_lead_entity(
            phone=msg.sender_phone,
            name=msg.sender_name,
        )

        # 2. Resolve or create active conversation session
        conversation = await self.conversation_repo.get_active_for_lead(lead.id)
        if not conversation:
            conversation = Conversation(
                lead_id=lead.id,
                channel="whatsapp",
                state=ConversationState.NEW_ENQUIRY.value,
                is_human_takeover=False,
                last_message_at=datetime.now(timezone.utc),
            )
            conversation = await self.conversation_repo.create(conversation)

        # 3. Store inbound message
        inbound_record = Message(
            conversation_id=conversation.id,
            external_message_id=msg.message_id,
            direction=MessageDirection.INBOUND.value,
            message_type=msg.message_type,
            content=msg.content,
            status=MessageProcessingStatus.PROCESSED.value,
            metadata_json=msg.raw_payload,
        )
        await self.message_repo.create(inbound_record)

        # 4. Check for Opt-Out intent (Compliance priority: always process STOP even during human takeover)
        user_text = msg.content.strip().lower()
        if user_text in ("stop", "unsubscribe", "optout", "opt out", "cancel"):
            lead.consent_status = "OPTED_OUT"
            await self.session.flush()
            await self.conversation_repo.update_state(conversation, ConversationState.OPTED_OUT)
            await FollowUpRepository(self.session).cancel_pending_for_lead(lead.id)
            reply_text = (
                "You have been unsubscribed from automated updates. "
                "You will not receive further messages. Send START at any time to reconnect with us."
            )
            await self._send_and_record_reply(conversation, lead.phone, reply_text)
            return {"action": "opted_out", "replied": True}

        # 5. Check for Human Takeover suppression
        if conversation.is_human_takeover:
            logger.info(f"Conversation {conversation.id} is under human takeover. Suppressing AI response.")
            return {
                "action": "human_suppressed",
                "lead_id": str(lead.id),
                "conversation_id": str(conversation.id),
                "replied": False,
            }

        # 6. Check for Human Agent Request
        if any(keyword in user_text for keyword in ("agent", "human", "representative", "manager", "call me", "person")):
            await self.conversation_repo.set_human_takeover(conversation, True)
            await self.conversation_repo.update_state(conversation, ConversationState.HUMAN_HANDOFF)
            reply_text = (
                "I've notified our Senior Property Advisor! 👤\n\n"
                "A specialist will review your requirements and reach out to you shortly. "
                "Feel free to reply with any specific questions or preferred callback times."
            )
            await self._send_and_record_reply(conversation, lead.phone, reply_text)
            return {"action": "human_handoff_initiated", "replied": True}

        # 7. Run SalesAgentV2 tool-calling orchestrator
        if msg.sender_name and not lead.name:
            lead.name = msg.sender_name
            await self.session.flush()

        reply_text = await self.agent_v2.handle_message(
            lead_id=str(lead.id),
            phone=lead.phone,
            conversation_id=str(conversation.id),
            text=msg.content,
            already_saved=True,
        )

        # Refresh lead to get latest score and qualification calculated during turn
        await self.session.refresh(lead)
        conv = await self.conversation_repo.get_by_id(conversation.id)
        current_state = conv.state if conv else conversation.state

        # Update conversation state according to progress
        if lead.lead_category == LeadCategory.HOT.value or (lead.preferred_location and lead.budget_max):
            new_state = ConversationState.PROPERTY_RECOMMENDATION.value
        else:
            new_state = ConversationState.REQUIREMENTS_COLLECTION.value

        if conv and conv.state != new_state and not conv.is_human_takeover:
            await self.conversation_repo.update_state(conv, ConversationState(new_state))
            current_state = new_state

        return {
            "action": "replied",
            "lead_id": str(lead.id),
            "lead_category": lead.lead_category,
            "lead_score": lead.lead_score,
            "state": current_state,
            "reply": reply_text,
            "matching_properties_count": 1,
        }

    async def _send_and_record_reply(
        self,
        conversation: Conversation,
        phone: str,
        text: str,
    ) -> Message:
        """Helper to send WhatsApp text and save outbound message record."""
        await whatsapp_client.send_text_message(to=phone, text=text)
        outbound_record = Message(
            conversation_id=conversation.id,
            external_message_id=None,
            direction=MessageDirection.OUTBOUND.value,
            message_type=MessageType.TEXT.value,
            content=text,
            status=MessageProcessingStatus.SENT.value,
            metadata_json={"automated": True},
        )
        return await self.message_repo.create(outbound_record)
