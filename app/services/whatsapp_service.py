"""
WhatsApp Webhook & Message Processing Service
Handles signature validation, payload parsing, deduplication, and routing.
"""

import hashlib
import hmac
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.config.settings import settings
from app.core.constants import MessageType
from app.core.logging import logger


class ParsedIncomingMessage(BaseModel):
    """Structured representation of an incoming WhatsApp message."""
    message_id: str
    sender_phone: str
    sender_name: Optional[str] = None
    message_type: str = MessageType.TEXT.value
    content: str = ""
    interactive_id: Optional[str] = None
    interactive_title: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: Optional[str] = None
    raw_payload: Dict[str, Any] = Field(default_factory=dict)


class ParsedStatusUpdate(BaseModel):
    """Structured representation of a WhatsApp delivery status notification."""
    message_id: str
    recipient_phone: str
    status: str
    timestamp: Optional[str] = None


class WhatsAppService:
    """Service for handling WhatsApp webhooks, signature security, and event parsing."""

    @staticmethod
    def verify_webhook_signature(
        raw_body: bytes,
        signature_header: Optional[str],
        app_secret: Optional[str] = None,
    ) -> bool:
        """
        Verify the X-Hub-Signature-256 header sent by Meta.
        Uses constant-time comparison to prevent timing attacks.
        """
        secret = app_secret or settings.WHATSAPP_APP_SECRET
        if not signature_header:
            logger.warning("Missing X-Hub-Signature-256 header on webhook request")
            return False

        if not signature_header.startswith("sha256="):
            logger.warning(f"Invalid signature format: {signature_header[:20]}")
            return False

        expected_signature = signature_header.split("sha256=", 1)[1]
        calculated_signature = hmac.new(
            key=secret.encode("utf-8"),
            msg=raw_body,
            digestmod=hashlib.sha256,
        ).hexdigest()

        is_valid = hmac.compare_digest(calculated_signature, expected_signature)
        if not is_valid:
            logger.warning("WhatsApp webhook signature validation failed")
        return is_valid

    @staticmethod
    def parse_webhook_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract messages and status updates from the nested Meta Cloud API webhook payload.
        Returns a dict: {"messages": List[ParsedIncomingMessage], "statuses": List[ParsedStatusUpdate]}
        """
        parsed_messages: List[ParsedIncomingMessage] = []
        parsed_statuses: List[ParsedStatusUpdate] = []

        entries = payload.get("entry", [])
        for entry in entries:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                if not value:
                    continue

                # 1. Extract contact profiles (maps wa_id -> profile name)
                contacts_map: Dict[str, str] = {}
                for contact in value.get("contacts", []):
                    wa_id = contact.get("wa_id")
                    profile_name = contact.get("profile", {}).get("name")
                    if wa_id and profile_name:
                        contacts_map[wa_id] = profile_name

                # 2. Extract inbound messages
                for msg in value.get("messages", []):
                    msg_id = msg.get("id")
                    sender_phone = msg.get("from")
                    if not msg_id or not sender_phone:
                        continue

                    msg_type = msg.get("type", "text")
                    sender_name = contacts_map.get(sender_phone)
                    content = ""
                    interactive_id = None
                    interactive_title = None
                    lat = None
                    lng = None

                    if msg_type == "text":
                        content = msg.get("text", {}).get("body", "").strip()

                    elif msg_type == "interactive":
                        interactive_data = msg.get("interactive", {})
                        sub_type = interactive_data.get("type")

                        if sub_type == "button_reply":
                            btn_reply = interactive_data.get("button_reply", {})
                            interactive_id = btn_reply.get("id")
                            interactive_title = btn_reply.get("title")
                            content = interactive_title or interactive_id or ""

                        elif sub_type == "list_reply":
                            list_reply = interactive_data.get("list_reply", {})
                            interactive_id = list_reply.get("id")
                            interactive_title = list_reply.get("title")
                            content = interactive_title or interactive_id or ""

                    elif msg_type == "location":
                        loc_data = msg.get("location", {})
                        lat = loc_data.get("latitude")
                        lng = loc_data.get("longitude")
                        loc_name = loc_data.get("name", "")
                        loc_address = loc_data.get("address", "")
                        content = f"Location: {loc_name} {loc_address} ({lat}, {lng})".strip()

                    elif msg_type in ("image", "document", "audio", "video"):
                        media_caption = msg.get(msg_type, {}).get("caption", "")
                        content = media_caption or f"[{msg_type.upper()} RECEIVED]"

                    parsed_messages.append(
                        ParsedIncomingMessage(
                            message_id=msg_id,
                            sender_phone=sender_phone,
                            sender_name=sender_name,
                            message_type=msg_type,
                            content=content,
                            interactive_id=interactive_id,
                            interactive_title=interactive_title,
                            latitude=lat,
                            longitude=lng,
                            timestamp=str(msg.get("timestamp")),
                            raw_payload=msg,
                        )
                    )

                # 3. Extract status receipts (sent, delivered, read, failed)
                for status_item in value.get("statuses", []):
                    status_id = status_item.get("id")
                    status_val = status_item.get("status")
                    recipient = status_item.get("recipient_id")
                    if status_id and status_val:
                        parsed_statuses.append(
                            ParsedStatusUpdate(
                                message_id=status_id,
                                recipient_phone=recipient or "",
                                status=status_val,
                                timestamp=str(status_item.get("timestamp")),
                            )
                        )

        return {"messages": parsed_messages, "statuses": parsed_statuses}


whatsapp_service = WhatsAppService()
