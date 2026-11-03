"""
Tool-calling SalesAgent (v2) for Prestige Realty.

The LLM decides what to do next. The code decides what is TRUE.
Facts (properties, slots, bookings) only ever come from tool results.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Set, Tuple
import uuid
from zoneinfo import ZoneInfo

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.core.constants import (
    ConversationState,
    LeadCategory,
    MessageDirection,
    MessageProcessingStatus,
    MessageType,
    PropertyStatus,
    SiteVisitStatus,
)
from app.core.logging import logger
from app.integrations.openrouter.client import openrouter_client
from app.integrations.whatsapp.client import whatsapp_client
from app.integrations.calcom.client import calcom_client
from app.models.conversation import Conversation
from app.models.lead import Lead
from app.models.message import Message
from app.models.property import Property
from app.models.site_visit import SiteVisit
from app.models.ai_decision import AIDecision
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.property_repository import PropertyRepository
from app.services.email_service import email_service
from app.services.image_library_service import image_library_service
from app.services.lead_service import LeadService
from app.services.property_service import PropertyService
from app.services.whatsapp_service import ParsedIncomingMessage

log = logging.getLogger(__name__)

IST = ZoneInfo("Asia/Kolkata")
MAX_TOOL_ROUNDS = 5
HISTORY_LIMIT = 20
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "sales_agent_system.md"

# ---------------------------------------------------------------------------
# Tool schemas (OpenAI-compatible, works through OpenRouter)
# ---------------------------------------------------------------------------
TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "update_lead_profile",
            "description": "Save any facts the customer just told you. Call it as soon as you learn something.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string"},
                    "preferred_location": {"type": "string"},
                    "property_type": {"type": "string", "enum": ["APARTMENT", "VILLA", "PLOT"]},
                    "bedroom_preference": {"type": "integer"},
                    "budget_min": {"type": "integer", "description": "In rupees"},
                    "budget_max": {"type": "integer", "description": "In rupees"},
                    "purchase_purpose": {"type": "string", "enum": ["SELF_USE", "INVESTMENT"]},
                    "purchase_timeline": {"type": "string", "enum": ["IMMEDIATE", "1_3_MONTHS", "3_6_MONTHS", "EXPLORING"]},
                    "funding_method": {"type": "string", "enum": ["SELF_FUNDED", "HOME_LOAN", "BOTH"]},
                    "email": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_properties",
            "description": "Find verified available properties. Omit fields you do not know. Returns closest alternatives if no exact match.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "property_type": {"type": "string"},
                    "bedrooms": {"type": "integer"},
                    "budget_max": {"type": "integer"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_property_images",
            "description": "Send photos of a property to the customer on WhatsApp. Use right after presenting a property.",
            "parameters": {
                "type": "object",
                "properties": {"property_id": {"type": "string"}},
                "required": ["property_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_available_slots",
            "description": "Get real bookable site-visit slots for the next few days.",
            "parameters": {
                "type": "object",
                "properties": {"property_id": {"type": "string"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_site_visit",
            "description": "Book a site visit. Needs a slot_id returned by get_available_slots and the customer's email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_id": {"type": "string"},
                    "slot_id": {"type": "string"},
                    "email": {"type": "string"},
                },
                "required": ["property_id", "slot_id", "email"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "handoff_to_human",
            "description": "Alert a human sales manager to call this customer.",
            "parameters": {
                "type": "object",
                "properties": {"reason": {"type": "string"}},
                "required": ["reason"],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# Protocols
# ---------------------------------------------------------------------------
class LLM(Protocol):
    async def chat(self, messages: list[dict], tools: list[dict]) -> dict:
        """POST to OpenRouter /chat/completions with tools; return the first choice's message dict."""


class Deps(Protocol):
    async def update_lead(self, lead_id: str, fields: dict) -> None: ...
    async def recalc_score(self, lead_id: str) -> tuple[int, str]: ...
    async def lead_snapshot(self, lead_id: str) -> dict: ...
    async def search_properties(self, **filters) -> list[dict]: ...
    async def get_property(self, property_id: str) -> Optional[dict]: ...
    async def property_image_urls(self, property_id: str, limit: int = 3) -> list[str]: ...
    async def send_text(self, to: str, text: str) -> None: ...
    async def send_image(self, to: str, url: str, caption: str) -> None: ...
    async def cal_slots(self, property_id: Optional[str]) -> list[dict]: ...
    async def cal_book(self, *, name: str, email: str, phone: str, slot: dict, property_id: str) -> dict: ...
    async def save_site_visit(self, lead_id: str, property_id: str, booking: dict) -> None: ...
    async def send_confirmation_email(self, lead_id: str, property_id: str, booking: dict) -> None: ...
    async def notify_human(self, lead_id: str, reason: str) -> None: ...
    async def recent_messages(self, conversation_id: str, limit: int) -> list[dict]: ...
    async def save_message(self, conversation_id: str, role: str, content: str) -> None: ...


@dataclass
class TurnContext:
    lead_id: str
    phone: str
    conversation_id: str
    offered_slots: dict[str, dict] = field(default_factory=dict)
    booking_failures: int = 0
    images_sent: set[str] = field(default_factory=set)


# ---------------------------------------------------------------------------
# Prompt rendering
# ---------------------------------------------------------------------------
REQUIRED_FIELDS = [
    "customer_name", "preferred_location", "property_type", "bedroom_preference",
    "budget_max", "purchase_purpose", "purchase_timeline", "funding_method", "email",
]


def render_system_prompt(snapshot: dict, score: int, tier: str) -> str:
    template = PROMPT_PATH.read_text(encoding="utf-8")
    known = {k: v for k, v in snapshot.items() if k in REQUIRED_FIELDS and v not in (None, "")}
    missing = [k for k in REQUIRED_FIELDS if k not in known]
    snapshot_txt = "\n".join(f"- {k}: {v}" for k, v in known.items()) or "- (nothing yet)"
    return (
        template.replace("{{now_ist}}", datetime.now(IST).strftime("%A, %d %B %Y, %I:%M %p"))
        .replace("{{lead_snapshot}}", snapshot_txt)
        .replace("{{score}}", str(score))
        .replace("{{tier}}", tier)
        .replace("{{missing_fields}}", ", ".join(missing) or "none")
    )


def _compact_property(p: dict) -> dict:
    """Only give the LLM what it may state as fact."""
    keys = (
        "id", "name", "location", "property_type", "bedrooms", "price_min", "price_max",
        "area_sqft", "amenities", "possession", "rera_id", "available", "highlights"
    )
    return {k: p[k] for k in keys if k in p}


# ---------------------------------------------------------------------------
# Production Database & Service Dependencies Adapter
# ---------------------------------------------------------------------------
class AppDeps:
    """Concrete adapter connecting SalesAgentV2 to SQLAlchemy models and system services."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.lead_repo = LeadRepository(session)
        self.conversation_repo = ConversationRepository(session)
        self.message_repo = MessageRepository(session)
        self.property_repo = PropertyRepository(session)
        self.lead_service = LeadService(session)
        self.property_service = PropertyService(session)

    async def update_lead(self, lead_id: str, fields: dict) -> None:
        lead = await self.lead_repo.get_by_id(uuid.UUID(lead_id))
        if not lead:
            return

        if "customer_name" in fields:
            lead.name = str(fields["customer_name"]).strip()
        if "preferred_location" in fields:
            lead.preferred_location = str(fields["preferred_location"]).strip()
        if "property_type" in fields:
            lead.property_type = str(fields["property_type"]).strip().upper()
        if "bedroom_preference" in fields:
            try:
                lead.bedroom_preference = int(fields["bedroom_preference"])
            except (ValueError, TypeError):
                pass
        if "budget_min" in fields:
            try:
                lead.budget_min = int(fields["budget_min"])
            except (ValueError, TypeError):
                pass
        if "budget_max" in fields:
            try:
                lead.budget_max = int(fields["budget_max"])
            except (ValueError, TypeError):
                pass
        if "purchase_purpose" in fields:
            lead.purchase_purpose = str(fields["purchase_purpose"]).strip()
        if "purchase_timeline" in fields:
            lead.purchase_timeline = str(fields["purchase_timeline"]).strip()
        if "funding_method" in fields:
            lead.financing_status = str(fields["funding_method"]).strip()
        if "email" in fields:
            em = str(fields["email"]).strip().lower()
            if "@" in em:
                lead.email = em

        await self.session.flush()

    async def recalc_score(self, lead_id: str) -> tuple[int, str]:
        lead = await self.lead_repo.get_by_id(uuid.UUID(lead_id))
        if not lead:
            return 0, "COLD"
        await self.lead_service.calculate_and_update_qualification(lead)
        return lead.lead_score, lead.lead_category

    async def lead_snapshot(self, lead_id: str) -> dict:
        lead = await self.lead_repo.get_by_id(uuid.UUID(lead_id))
        if not lead:
            return {}
        return {
            "customer_name": lead.name,
            "preferred_location": lead.preferred_location,
            "property_type": lead.property_type,
            "bedroom_preference": lead.bedroom_preference,
            "budget_min": lead.budget_min,
            "budget_max": lead.budget_max,
            "purchase_purpose": lead.purchase_purpose,
            "purchase_timeline": lead.purchase_timeline,
            "funding_method": lead.financing_status,
            "email": lead.email,
        }

    async def search_properties(self, **filters) -> list[dict]:
        query = select(Property)
        clauses = []

        loc = filters.get("location")
        if loc:
            loc_norm = loc.lower().replace("hyderabad", "").strip()
            clauses.append(Property.location.ilike(f"%{loc_norm}%"))

        ptype = filters.get("property_type")
        if ptype:
            clauses.append(Property.property_type.ilike(f"%{ptype}%"))

        beds = filters.get("bedrooms")
        if beds is not None:
            clauses.append(Property.bedrooms == int(beds))

        b_max = filters.get("budget_max")
        if b_max is not None:
            # Allow properties whose price_min is within or close to budget_max
            clauses.append(Property.price_min <= int(b_max) * 1.15)

        if clauses:
            query = query.where(and_(*clauses))

        res = await self.session.execute(query.limit(6))
        props = res.scalars().all()

        results = []
        for p in props:
            results.append({
                "id": str(p.id),
                "name": p.name,
                "location": p.location,
                "property_type": str(p.property_type),
                "bedrooms": p.bedrooms,
                "price_min": p.price_min,
                "price_max": p.price_max,
                "area_sqft": p.area_sqft,
                "amenities": p.amenities or [],
                "available": p.status == PropertyStatus.AVAILABLE.value,
                "possession": (p.metadata_json or {}).get("possession", "Ready / In Progress"),
                "rera_id": (p.metadata_json or {}).get("rera_id", "PRM/KA/RERA/1251"),
                "highlights": f"By {(p.metadata_json or {}).get('builder', 'Prestige Group')}",
            })
        return results

    async def get_property(self, property_id: str) -> Optional[dict]:
        try:
            pid = uuid.UUID(property_id)
        except ValueError:
            return None
        p = await self.property_repo.get_by_id(pid)
        if not p:
            return None
        return {
            "id": str(p.id),
            "name": p.name,
            "location": p.location,
            "property_type": str(p.property_type),
            "bedrooms": p.bedrooms,
            "price_min": p.price_min,
            "price_max": p.price_max,
            "area_sqft": p.area_sqft,
            "amenities": p.amenities or [],
            "available": p.status == PropertyStatus.AVAILABLE.value,
            "possession": (p.metadata_json or {}).get("possession", "Ready"),
            "rera_id": (p.metadata_json or {}).get("rera_id", "PRM/KA/RERA/1251"),
            "highlights": f"By {(p.metadata_json or {}).get('builder', 'Prestige Group')}",
        }

    async def property_image_urls(self, property_id: str, limit: int = 3) -> list[str]:
        p = await self.get_property(property_id)
        if not p:
            return []
        
        # Check if property record has direct images
        prop_entity = await self.property_repo.get_by_id(uuid.UUID(property_id))
        if prop_entity and prop_entity.images:
            return prop_entity.images[:limit]

        # Otherwise fetch verified neighbourhood images for this location from image_library_service
        loc = p.get("location", "")
        imgs = image_library_service.get_images_for_location(loc, limit=limit)
        return [img.url for img in imgs]

    async def send_text(self, to: str, text: str) -> None:
        await whatsapp_client.send_text_message(to=to, text=text)

    async def send_image(self, to: str, url: str, caption: str, conversation_id: Optional[str] = None) -> None:
        await whatsapp_client.send_image_message(to=to, image_url=url, caption=caption)
        if conversation_id:
            try:
                media_record = Message(
                    id=uuid.uuid4(),
                    conversation_id=uuid.UUID(conversation_id),
                    external_message_id=None,
                    direction=MessageDirection.OUTBOUND.value,
                    message_type=MessageType.IMAGE.value,
                    content=caption,
                    status=MessageProcessingStatus.SENT.value,
                    metadata_json={"media_url": url, "caption": caption},
                )
                await self.message_repo.create(media_record)
            except Exception as e:
                logger.warning(f"Could not record image message in db: {e}")

    async def cal_slots(self, property_id: Optional[str]) -> list[dict]:
        dates = await calcom_client.get_available_dates(days_ahead=5)
        slots = []
        for d in dates[:3]:
            day_slots = await calcom_client.get_available_slots_for_date(d["date"])
            for s in day_slots[:2]:  # 2 per day
                slot_id = f"slot_{s.time.replace(':', '').replace('-', '').replace('+', '_')}"
                slots.append({
                    "id": slot_id,
                    "start_iso": s.time,
                    "label": f"{s.formatted_date} at {s.formatted_time}",
                })
        return slots

    async def cal_book(self, *, name: str, email: str, phone: str, slot: dict, property_id: str) -> dict:
        start_time = slot.get("start_iso") or slot.get("id")
        result = await calcom_client.create_booking(
            start_time=start_time,
            attendee_name=name,
            attendee_email=email,
            attendee_phone=phone,
            notes=f"Property: {property_id}",
        )
        if not result.success:
            raise Exception(result.error_message or "Booking failed")
        return {
            "uid": result.booking_uid or result.booking_id,
            "start_iso": result.start_time or start_time,
            "label": slot.get("label", "Upcoming appointment"),
        }

    async def save_site_visit(self, lead_id: str, property_id: str, booking: dict) -> None:
        try:
            p_uuid = uuid.UUID(property_id)
        except Exception:
            # If property_id is not a valid UUID, find first available property
            res = await self.session.execute(select(Property).limit(1))
            first_p = res.scalars().first()
            p_uuid = first_p.id if first_p else uuid.uuid4()

        start_dt = datetime.now()
        start_iso = booking.get("start_iso")
        if start_iso:
            try:
                start_dt = datetime.fromisoformat(start_iso)
            except Exception:
                pass

        visit = SiteVisit(
            id=uuid.uuid4(),
            lead_id=uuid.UUID(lead_id),
            property_id=p_uuid,
            scheduled_time=start_dt,
            duration_minutes=45,
            status=SiteVisitStatus.CONFIRMED.value,
            google_calendar_event_id=booking.get("uid"),
            notes=f"Cal.com Ref: {booking.get('uid')}",
        )
        self.session.add(visit)
        await self.session.flush()

    async def send_confirmation_email(self, lead_id: str, property_id: str, booking: dict) -> None:
        lead = await self.lead_repo.get_by_id(uuid.UUID(lead_id))
        prop = await self.get_property(property_id)
        if not lead or not lead.email:
            return

        prop_name = prop.get("name", "Prestige Realty Property") if prop else "Prestige Property"
        prop_loc = prop.get("location", "Hyderabad") if prop else "Hyderabad"
        label = booking.get("label", "Site Visit")

        await email_service.send_booking_confirmation(
            to_email=lead.email,
            customer_name=lead.name or "Valued Customer",
            property_name=prop_name,
            location=prop_loc,
            scheduled_date_str=label,
            scheduled_time_str="45-minute tour",
            booking_ref=booking.get("uid", "CAL-CONFIRMED"),
            reschedule_url=settings.CAL_COM_BOOKING_URL,
        )

    async def notify_human(self, lead_id: str, reason: str) -> None:
        lead = await self.lead_repo.get_by_id(uuid.UUID(lead_id))
        conv = await self.conversation_repo.get_active_for_lead(uuid.UUID(lead_id))
        if conv:
            await self.conversation_repo.set_human_takeover(conv, True)
            await self.conversation_repo.update_state(conv, ConversationState.HUMAN_HANDOFF)

        decision = AIDecision(
            id=uuid.uuid4(),
            decision_type="HUMAN_HANDOFF",
            input_context_summary=f"Handoff requested: {reason}",
            output_decision={"reason": reason, "handover": True},
            reasoning_summary=f"Automated handoff triggered by customer intent: {reason}",
            lead_id=uuid.UUID(lead_id),
            conversation_id=conv.id if conv else None,
        )
        self.session.add(decision)
        await self.session.flush()

    async def recent_messages(self, conversation_id: str, limit: int) -> list[dict]:
        msgs = await self.message_repo.get_recent_history(uuid.UUID(conversation_id), limit=limit)
        formatted = []
        for m in msgs:
            role = "user" if m.direction == MessageDirection.INBOUND.value else "assistant"
            formatted.append({"role": role, "content": m.content})
        return formatted

    async def save_message(self, conversation_id: str, role: str, content: str) -> None:
        direction = MessageDirection.INBOUND.value if role == "user" else MessageDirection.OUTBOUND.value
        msg = Message(
            id=uuid.uuid4(),
            conversation_id=uuid.UUID(conversation_id),
            external_message_id=None,
            direction=direction,
            message_type=MessageType.TEXT.value,
            content=content,
            status=MessageProcessingStatus.PROCESSED.value if role == "user" else MessageProcessingStatus.SENT.value,
            metadata_json={"source": "sales_agent_v2"},
        )
        await self.message_repo.create(msg)


# ---------------------------------------------------------------------------
# SalesAgentV2 Orchestrator
# ---------------------------------------------------------------------------
class SalesAgentV2:
    def __init__(self, llm: LLM, deps: Deps):
        self.llm = llm
        self.d = deps

    async def handle_message(self, *, lead_id: str, phone: str, conversation_id: str, text: str, already_saved: bool = False) -> str:
        ctx = TurnContext(lead_id=lead_id, phone=phone, conversation_id=conversation_id)
        if not already_saved:
            await self.d.save_message(conversation_id, "user", text)

        reply: Optional[str] = None
        try:
            reply = await self._run_llm_turn(ctx, text)
        except Exception:
            log.exception("LLM turn failed, using fallback")

        if not reply or not reply.strip():
            reply = await self._fallback_reply(ctx)

        clean_reply = reply.strip()
        await self.d.send_text(phone, clean_reply)
        await self.d.save_message(conversation_id, "assistant", clean_reply)
        return clean_reply

    async def _run_llm_turn(self, ctx: TurnContext, text: str) -> Optional[str]:
        score, tier = await self.d.recalc_score(ctx.lead_id)
        snapshot = await self.d.lead_snapshot(ctx.lead_id)
        history = await self.d.recent_messages(ctx.conversation_id, HISTORY_LIMIT)

        # history already contains the new user message because we saved it above
        messages: list[dict] = [{"role": "system", "content": render_system_prompt(snapshot, score, tier)}]
        messages += [{"role": m["role"], "content": m["content"]} for m in history]

        for _ in range(MAX_TOOL_ROUNDS):
            msg = await self.llm.chat(messages, TOOLS)
            tool_calls = msg.get("tool_calls") or []
            if not tool_calls:
                return msg.get("content") or ""

            messages.append({k: msg[k] for k in ("role", "content", "tool_calls") if k in msg})
            for tc in tool_calls:
                name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"].get("arguments") or "{}")
                    result = await self._execute_tool(ctx, name, args)
                except Exception as e:
                    log.exception("tool %s failed", name)
                    result = {"ok": False, "error": str(e)}
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                })
        return None  # too many rounds -> fallback

    # ------------------------------------------------------------------ tools
    async def _execute_tool(self, ctx: TurnContext, name: str, a: dict) -> dict:
        if name == "update_lead_profile":
            fields = {k: v for k, v in a.items() if v not in (None, "")}
            await self.d.update_lead(ctx.lead_id, fields)
            score, tier = await self.d.recalc_score(ctx.lead_id)
            return {"ok": True, "saved": list(fields), "score": score, "tier": tier}

        if name == "search_properties":
            filters = {k: v for k, v in a.items() if v not in (None, "")}
            found = await self.d.search_properties(**filters)
            exact = [p for p in found if p.get("available", True)]
            if exact:
                return {"ok": True, "match_type": "exact", "properties": [_compact_property(p) for p in exact[:3]]}
            # relax filters step by step: budget, then bedrooms, then location
            for drop in ("budget_max", "bedrooms", "location"):
                filters.pop(drop, None)
                alt = [p for p in await self.d.search_properties(**filters) if p.get("available", True)]
                if alt:
                    return {"ok": True, "match_type": f"closest_alternatives_relaxed_{drop}",
                            "properties": [_compact_property(p) for p in alt[:3]]}
            return {"ok": True, "match_type": "none", "properties": []}

        if name == "send_property_images":
            pid = a["property_id"]
            if pid in ctx.images_sent:
                return {"ok": True, "note": "already sent in this turn"}
            prop = await self.d.get_property(pid)
            urls = await self.d.property_image_urls(pid, limit=3)
            if not prop or not urls:
                return {"ok": False, "error": "no images stored for this property"}
            for i, url in enumerate(urls):
                caption = prop["name"] if i else f"📍 {prop['name']} - {prop.get('location', '')}\n(Illustrative neighbourhood architecture)"
                await self.d.send_image(ctx.phone, url, caption, ctx.conversation_id)
            ctx.images_sent.add(pid)
            return {"ok": True, "sent": len(urls)}

        if name == "get_available_slots":
            slots = await self.d.cal_slots(a.get("property_id"))
            ctx.offered_slots = {s["id"]: s for s in slots}
            return {"ok": True, "slots": [{"slot_id": s["id"], "label": s["label"]} for s in slots[:6]]}

        if name == "book_site_visit":
            slot = ctx.offered_slots.get(a["slot_id"])
            if not slot:
                # Slot might have been offered in a previous turn; re-fetch from Cal.com
                all_slots = await self.d.cal_slots(a.get("property_id"))
                for s in all_slots:
                    if s["id"] == a["slot_id"] or a["slot_id"] in s.get("start_iso", ""):
                        slot = s
                        break
            if not slot:
                return {"ok": False, "error": "unknown slot_id. Call get_available_slots first."}
            snapshot = await self.d.lead_snapshot(ctx.lead_id)
            try:
                booking = await self.d.cal_book(
                    name=snapshot.get("customer_name") or "Customer",
                    email=a["email"], phone=ctx.phone, slot=slot, property_id=a["property_id"],
                )
            except Exception as e:
                ctx.booking_failures += 1
                log.exception("cal booking failed")
                out = {"ok": False, "error": f"booking failed: {e}"}
                if ctx.booking_failures >= 2:
                    out["fallback"] = f"Send the public booking link now: {settings.CAL_COM_BOOKING_URL}"
                return out
            await self.d.update_lead(ctx.lead_id, {"email": a["email"]})
            await self.d.save_site_visit(ctx.lead_id, a["property_id"], booking)
            await self.d.send_confirmation_email(ctx.lead_id, a["property_id"], booking)
            return {"ok": True, "booked": True, "when": slot["label"], "booking_ref": booking.get("uid")}

        if name == "handoff_to_human":
            await self.d.notify_human(ctx.lead_id, a.get("reason", ""))
            return {"ok": True, "note": "Sales manager alerted. Tell the customer they will get a call today."}

        return {"ok": False, "error": f"unknown tool {name}"}

    # --------------------------------------------------------------- fallback
    async def _fallback_reply(self, ctx: TurnContext) -> str:
        """Used only when the LLM fails. Still moves the lead forward, never a dead end."""
        score, tier = await self.d.recalc_score(ctx.lead_id)
        snap = await self.d.lead_snapshot(ctx.lead_id)
        name = snap.get("customer_name") or ""
        greet = f"Thanks {name}! " if name else "Thanks! "

        if tier == "HOT" or all(snap.get(k) for k in ("preferred_location", "budget_max")):
            try:
                slots = await self.d.cal_slots(None)
                if slots:
                    opts = " or ".join(s["label"] for s in slots[:2])
                    return f"{greet}I can arrange a site visit for you. Would {opts} work?"
            except Exception:
                log.exception("fallback slots failed")

        order = [
            ("customer_name", "May I know your name?"),
            ("preferred_location", "Which area are you looking at? (Gachibowli, Kokapet, Financial District...)"),
            ("property_type", "Are you looking for an apartment, villa or plot?"),
            ("bedroom_preference", "How many bedrooms do you need? (2 BHK, 3 BHK, or 4 BHK)"),
            ("budget_max", "What budget range are you comfortable with? (Below ₹1 Cr, ₹1–1.5 Cr, ₹1.5–2 Cr, Above ₹2 Cr)"),
            ("purchase_purpose", "Are you buying for your own use or as an investment? (Self-use or Investment)"),
            ("purchase_timeline", "When are you planning to buy? (Immediately, Within 3 months, Within 6 months, or Just exploring)"),
            ("funding_method", "How are you planning to fund the purchase? (Self-funded, Home loan, or Both)"),
        ]
        for key, q in order:
            if not snap.get(key):
                return f"{greet}{q}"
        return f"{greet}Would you like to see the matching properties on a site visit this week?"
