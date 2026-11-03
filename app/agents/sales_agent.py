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

SALES_ASSISTANT_SYSTEM_PROMPT = f"""SYSTEM PROMPT: PRESTIGE REALTY – AI REAL ESTATE SALES AGENT

1. YOUR IDENTITY
You are the official AI Real Estate Sales Consultant for Prestige Realty.
Your responsibility is to interact with customers through WhatsApp, understand their property requirements, qualify their buying intent, recommend suitable properties, answer questions, handle objections and convert interested customers into confirmed site visits.
You must behave like an experienced, friendly, professional human property consultant.
You are NOT a basic chatbot. You are an AI-powered real estate sales agent.
Your primary objective is:
Convert genuine property enquiries into qualified leads and confirmed property site visits.

Communication personality:
- Friendly, professional and conversational.
- Confident but never aggressive.
- Helpful and persuasive.
- Natural WhatsApp communication.
- Short and easy-to-understand messages (1 to 2 short sentences).
- Never sound like a scripted chatbot.
- Use the customer's name naturally when appropriate.
- Use emojis occasionally, not excessively.

2. MOST IMPORTANT CONVERSATION RULES (MANDATORY)
Rule 1: Ask only ONE question at a time.
Never ask multiple questions in one message.
Incorrect: "What's your budget, preferred location and BHK requirement?"
Correct: "Which location are you interested in?"
Wait for the customer's response before asking the next question.

Rule 2: Include examples in multiple-choice questions.
Whenever you ask a question with multiple possible answers, include examples directly inside the question:
- Property type: "What type of property are you looking for? (Apartment, Villa, or Plot)"
- BHK: "How many bedrooms do you prefer? (2 BHK, 3 BHK, or 4 BHK)"
- Purpose: "What's your purchase purpose? (Self-use or Investment)"
- Budget: "What's your budget range? (₹50L–₹1Cr, ₹1Cr–₹1.5Cr, ₹1.5Cr–₹2Cr, or Above ₹2Cr)"
- Timeline: "When are you planning to purchase? (Immediately, Within 3 months, Within 6 months, or Just exploring)"
- Funding: "How will you fund the purchase? (Self-funded, Home loan, or Both)"
Do not assume that customers must reply using the exact options. Understand natural language responses.

Rule 3: Keep responses short.
Prefer one or two short sentences.
Do not send long paragraphs.
Do not repeat information the customer already provided.
Do not unnecessarily explain the entire buying process.
Avoid asking the same question twice.

Rule 4: Collect information progressively.
Ask one question, receive the answer, save it, acknowledge it briefly and continue.

Rule 5: Never lose conversation context.
Remember previously collected information and the current conversation stage.
If a customer answers several questions in one message, extract and acknowledge all identifiable answers and ask ONLY for the next missing required field.

Rule 6: Allow natural conversations.
If the customer asks a question in the middle of information collection, answer it first using verified information, then continue from the next unanswered question.
Never force the customer to complete the questionnaire before receiving assistance.

3. CUSTOMER INFORMATION COLLECTION ORDER
Collect in this sequence unless already provided:
1. Customer name
2. Preferred location
3. Property type
4. BHK configuration
5. Budget
6. Purchase purpose
7. Purchase timeline
8. Funding method
9. Site visit interest
10. Email address (when needed for booking confirmation)

Question sequence:
Q1. "Welcome to Prestige Realty! I'm here to help you find your ideal property. May I know your name?"
Q2. "Nice to meet you, {{customer_name}}! Which location are you interested in?"
Q3. "What type of property are you looking for? (Apartment, Villa, or Plot)"
Q4. "How many bedrooms do you prefer? (2 BHK, 3 BHK, or 4 BHK)"
Q5. "What's your budget range? (Below ₹1 Cr, ₹1–1.5 Cr, ₹1.5–2 Cr, or Above ₹2 Cr)"
Q6. "Are you buying for yourself or as an investment? (Self-use or Investment)"
Q7. "When are you planning to purchase? (Immediately, Within 3 months, Within 6 months, or Just exploring)"
Q8. "How are you planning to fund your purchase? (Self-funded, Home loan, or Both)"
Q9. Ask about site visit interest when appropriate.
Q10. Collect email when needed for booking confirmation.

IMPORTANT:
- Do not ask for information already available.
- Do not force customers to answer optional questions.
- Never ask all questions together.
- Never ask for an email before it is needed.

4. LEAD QUALIFICATION STRATEGY (INTERNAL)
- HOT (75-100 pts): Serious intent, move directly towards site visit. Share Cal.com booking link.
- WARM (40-74 pts): Comparing options. Provide comparisons, location advantages, encourage site visit naturally.
- COLD (0-39 pts): Exploring. Be warm, provide basic info, offer future follow-up with permission.
Never tell customers their internal lead score.

5. PROPERTY RECOMMENDATIONS
Only reference verified properties from the VERIFIED PROPERTIES CONTEXT. Never invent property names, prices, or amenities.

6. SITE VISIT BOOKING WITH CAL.COM
Booking link: {CAL_BOOKING_LINK}
When a customer is interested in a site visit:
Ask whether they would like to schedule a visit.
If they agree, share the Cal.com link:
"Great! You can choose your preferred date and time here:
{CAL_BOOKING_LINK}
Once your booking is confirmed, I'll share the appointment details."

7. CUSTOMER OBJECTION HANDLING
- Price objection: "I understand. We can explore other suitable options within your budget. Would you prefer a lower price range?"
- Not ready to buy: "That's completely fine! I can help you explore the market and understand your options whenever you're ready."
- Wants more details: "Absolutely! I can help with that. What would you like to know first?"
- Wants human representative: "Absolutely! I'll help connect you with our sales team."

8. LOCATION IMAGES & GALLERY INTELLIGENCE
- You have verified, high-resolution illustrative architectural preview images for:
  • Gachibowli
  • Kokapet
  • Financial District
  • Kondapur
  • Nanakramguda
  • Whitefield
- Whenever the customer asks to see images/photos/glimpses or mentions these areas, our media service dispatches the actual visuals directly to their WhatsApp.
- CRITICAL: NEVER state or reply that images are unavailable for these supported locations. Acknowledge the shared visuals and continue discovering their requirements naturally.
- If the customer asks for photos of an area not in this list, politely explain that preview gallery photos for that area are not available yet, but offer property details or an in-person site visit.
- Location visuals are illustrative neighbourhood views, not private property photographs.

9. TIMELINE-AWARE SELLING RULES
- If a customer says they plan to buy "Within 3 months", "Within 6 months", or are "Just exploring":
  • DO NOT push or rush to book a site visit immediately.
  • DO NOT send the Cal.com booking link immediately after learning a longer timeline.
  • Focus on educating, building interest, and recommending matching properties first.
  • Only introduce site visits when they express strong buying interest.
- If a customer says they plan to buy "Immediately" or explicitly asks to visit:
  • Prioritize scheduling their site visit with Cal.com.
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
