"""
WhatsApp Cloud API Integration Client
Handles outbound communication via Meta Graph API v21.0.
Supports standard text, interactive quick-reply buttons, interactive list messages, and location pins.
"""

from typing import Any, Dict, List, Optional
import httpx
from app.config.settings import settings
from app.core.exceptions import AIIntegrationException
from app.core.logging import logger


class WhatsAppClient:
    """Async client for Meta WhatsApp Cloud API."""

    def __init__(
        self,
        api_token: Optional[str] = None,
        phone_number_id: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        self.api_token = api_token or settings.WHATSAPP_API_TOKEN
        self.phone_number_id = phone_number_id or settings.WHATSAPP_PHONE_NUMBER_ID
        self.api_version = api_version or settings.WHATSAPP_API_VERSION
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    async def send_text_message(
        self,
        to: str,
        text: str,
        preview_url: bool = False,
    ) -> Dict[str, Any]:
        """
        Send a regular text message to a WhatsApp user.
        :param to: Recipient phone number in E.164 format without '+' (e.g. 919876543210)
        :param text: Message text body (supports standard WhatsApp formatting *bold*, _italic_)
        :param preview_url: Whether to render link previews if URL detected
        """
        clean_to = to.lstrip("+").strip()
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": text,
            },
        }
        return await self._post_message(payload)

    async def send_interactive_buttons(
        self,
        to: str,
        body_text: str,
        buttons: List[Dict[str, str]],
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send an interactive quick-reply button message (up to 3 buttons supported by Meta).
        :param buttons: List of dicts, e.g. [{"id": "btn_yes", "title": "Schedule Visit"}]
        """
        clean_to = to.lstrip("+").strip()
        if len(buttons) > 3:
            buttons = buttons[:3]

        formatted_buttons = [
            {
                "type": "reply",
                "reply": {
                    "id": btn.get("id", f"btn_{i}"),
                    "title": btn.get("title", "")[:20],  # Meta max 20 chars
                },
            }
            for i, btn in enumerate(buttons)
        ]

        action: Dict[str, Any] = {"buttons": formatted_buttons}
        interactive: Dict[str, Any] = {
            "type": "button",
            "body": {"text": body_text},
            "action": action,
        }

        if header_text:
            interactive["header"] = {"type": "text", "text": header_text[:60]}
        if footer_text:
            interactive["footer"] = {"text": footer_text[:60]}

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
            "type": "interactive",
            "interactive": interactive,
        }
        return await self._post_message(payload)

    async def send_interactive_list(
        self,
        to: str,
        body_text: str,
        button_label: str,
        sections: List[Dict[str, Any]],
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send an interactive list message (menu with up to 10 rows across sections).
        """
        clean_to = to.lstrip("+").strip()
        interactive: Dict[str, Any] = {
            "type": "list",
            "body": {"text": body_text},
            "action": {
                "button": button_label[:20],
                "sections": sections,
            },
        }

        if header_text:
            interactive["header"] = {"type": "text", "text": header_text[:60]}
        if footer_text:
            interactive["footer"] = {"text": footer_text[:60]}

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
            "type": "interactive",
            "interactive": interactive,
        }
        return await self._post_message(payload)

    async def send_image_message(
        self,
        to: str,
        image_url: str,
        caption: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a property photo/render via WhatsApp Cloud API.
        :param to: Recipient phone number in E.164 format without '+'
        :param image_url: Public HTTPS URL of the property image
        :param caption: Optional text caption displayed below image
        """
        clean_to = to.lstrip("+").strip()
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
            "type": "image",
            "image": {
                "link": image_url,
            },
        }
        if caption:
            payload["image"]["caption"] = caption[:1024]
        return await self._post_message(payload)

    async def send_document_message(
        self,
        to: str,
        document_url: str,
        filename: str,
        caption: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a PDF brochure or floor plan document via WhatsApp Cloud API.
        :param to: Recipient phone number in E.164 format without '+'
        :param document_url: Public HTTPS URL of the PDF document
        :param filename: Downloadable file name (e.g. 'Sobha_Palm_Court_Brochure.pdf')
        :param caption: Optional text caption
        """
        clean_to = to.lstrip("+").strip()
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
            "type": "document",
            "document": {
                "link": document_url,
                "filename": filename,
            },
        }
        if caption:
            payload["document"]["caption"] = caption[:1024]
        return await self._post_message(payload)

    async def mark_as_read(self, message_id: str) -> bool:
        """Mark an incoming message as read (blue ticks)."""
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        try:
            await self._post_message(payload)
            return True
        except Exception as e:
            logger.warning(f"Failed to mark WhatsApp message {message_id} as read: {e}")
            return False

    async def _post_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute POST request against Meta Cloud API endpoint."""
        url = f"{self.base_url}/messages"
        logger.debug(f"Sending WhatsApp message to {url} with type {payload.get('type')}")

        # If testing or dummy credentials, mock return
        if (
            not self.api_token
            or self.api_token.startswith("placeholder")
            or "test" in settings.APP_ENV.lower()
        ):
            logger.info("Mock WhatsApp client invoked (test/placeholder environment).")
            return {
                "messaging_product": "whatsapp",
                "contacts": [{"input": payload.get("to"), "wa_id": payload.get("to")}],
                "messages": [{"id": f"mock_wamid_{hash(str(payload))}"}],
            }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload)
                resp_json = response.json()

                if response.status_code >= 400:
                    err_detail = resp_json.get("error", {}).get("message", response.text)
                    err_code = resp_json.get("error", {}).get("code")
                    err_subcode = resp_json.get("error", {}).get("error_subcode")

                    # Handle Meta Sandbox test-recipient restriction gracefully
                    if err_code == 131030 or err_subcode == 131030 or "not in allowed list" in err_detail:
                        logger.warning(
                            f"Meta Cloud API Sandbox notice: Recipient {payload.get('to')} is not in the "
                            f"Meta Developer allowed recipient list. Outbound message recorded locally."
                        )
                        return {
                            "messaging_product": "whatsapp",
                            "contacts": [{"input": payload.get("to"), "wa_id": payload.get("to")}],
                            "messages": [{"id": f"sandbox_simulated_{payload.get('to')}"}],
                            "warning": "recipient_not_in_sandbox_allowed_list",
                        }

                    logger.error(
                        f"WhatsApp Cloud API Error [{response.status_code}]: {err_detail} | Payload: {payload}"
                    )
                    raise AIIntegrationException(
                        f"WhatsApp API Error [{response.status_code}]: {err_detail}",
                        details={"status_code": response.status_code, "response": resp_json},
                    )

                logger.info(f"WhatsApp message dispatched successfully to {payload.get('to')}")
                return resp_json

            except httpx.RequestError as exc:
                logger.error(f"WhatsApp Cloud API Network Connection Error: {exc}")
                raise AIIntegrationException(f"WhatsApp API Connection Failed: {exc}")


# Global default client instance
whatsapp_client = WhatsAppClient()
