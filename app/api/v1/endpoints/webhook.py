"""
WhatsApp Webhook Ingestion & Dispatch Endpoints
Provides Meta challenge handshake (GET) and secure HMAC-authenticated event ingestion (POST).
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.sales_agent import SalesAgent
from app.config.settings import settings
from app.core.logging import logger
from app.db.session import get_db_session
from app.repositories.webhook_repository import WebhookRepository
from app.services.whatsapp_service import whatsapp_service

router = APIRouter(prefix="/webhook", tags=["WhatsApp Webhook"])


@router.get("", summary="Meta Webhook Verification Handshake")
async def verify_webhook(
    mode: Optional[str] = Query(None, alias="hub.mode"),
    challenge: Optional[str] = Query(None, alias="hub.challenge"),
    verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
):
    """
    Verification challenge handshake initiated by Meta when subscribing or updating webhook URLs.
    Validates hub.mode == 'subscribe' and hub.verify_token matches configured secret.
    Returns plain-text challenge string upon success.
    """
    logger.info(f"Webhook verification challenge received: mode={mode}, token_match={verify_token == settings.WHATSAPP_VERIFY_TOKEN}")

    if mode == "subscribe" and verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        if not challenge:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing hub.challenge query parameter.",
            )
        return Response(content=challenge, media_type="text/plain", status_code=status.HTTP_200_OK)

    logger.warning(f"Webhook verification rejected: invalid token or mode (expected token '{settings.WHATSAPP_VERIFY_TOKEN}')")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Verification token mismatch or invalid subscription mode.",
    )


@router.post("", summary="Inbound WhatsApp Webhook Receiver")
async def receive_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Ingests inbound Meta WhatsApp events (messages, button clicks, status receipts).
    - Verifies HMAC-SHA256 signature against WHATSAPP_APP_SECRET.
    - Performs idempotency checks to prevent duplicate message ingestion.
    - Dispatches messages to the autonomous Real Estate Sales Agent.
    """
    raw_body = await request.body()

    # 1. Signature Security Validation
    # Allow bypass in testing environment only if explicitly configured
    bypass_sig = settings.APP_ENV == "testing" and not x_hub_signature_256
    if not bypass_sig:
        is_valid = whatsapp_service.verify_webhook_signature(
            raw_body=raw_body,
            signature_header=x_hub_signature_256,
        )
        if not is_valid:
            logger.error("Unauthorized webhook call: Invalid X-Hub-Signature-256")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature.",
            )

    # 2. JSON Payload Parsing
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Malformed JSON in webhook request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed JSON payload.",
        )

    # 3. Parse Inbound Messages & Delivery Receipts
    parsed = whatsapp_service.parse_webhook_payload(payload)
    messages = parsed.get("messages", [])
    statuses = parsed.get("statuses", [])

    webhook_repo = WebhookRepository(session)
    sales_agent = SalesAgent(session)
    processed_count = 0
    duplicate_count = 0

    # 4. Process Incoming Messages with Idempotency
    for msg in messages:
        # Check if already ingested (Meta retry protection)
        existing_event = await webhook_repo.get_by_event_id(msg.message_id)
        if existing_event:
            logger.info(f"Duplicate message ignored: {msg.message_id}")
            duplicate_count += 1
            continue

        # Record incoming event audit (safely handle concurrent Meta retries)
        try:
            event_record = await webhook_repo.record_event(
                event_id=msg.message_id,
                payload=msg.raw_payload,
                provider="whatsapp",
                status="PROCESSING",
            )
        except Exception as e:
            # Check if this is an integrity / duplicate key violation from concurrent delivery
            await session.rollback()
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                logger.info(f"Concurrent duplicate message ignored: {msg.message_id}")
                duplicate_count += 1
                continue
            raise

        try:
            # Dispatch to autonomous agent
            await sales_agent.process_incoming_message(msg)
            await webhook_repo.mark_processed(event_record, status="PROCESSED")
            processed_count += 1
        except Exception as e:
            logger.error(f"Error handling message {msg.message_id}: {e}", exc_info=True)
            await session.rollback()
            try:
                await webhook_repo.mark_processed(event_record, status="FAILED")
            except Exception:
                pass

    # 5. Process Delivery Receipts (if any)
    for stat in statuses:
        logger.debug(f"WhatsApp status receipt: message {stat.message_id} -> {stat.status}")

    return {
        "status": "success",
        "processed_messages": processed_count,
        "duplicate_messages": duplicate_count,
        "status_updates": len(statuses),
    }
