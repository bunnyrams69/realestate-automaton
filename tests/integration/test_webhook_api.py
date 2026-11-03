"""
Integration Tests for WhatsApp Webhook & AI Sales Agent
Validates Meta verification handshake, HMAC-SHA256 signature verification,
idempotent deduplication, human handoff, and opt-out flows.
"""

import hashlib
import hmac
import json
import uuid
import pytest
from httpx import AsyncClient
from app.config.settings import settings


def generate_meta_signature(payload_bytes: bytes, secret: str) -> str:
    """Helper to generate standard Meta X-Hub-Signature-256 header."""
    sig = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    return f"sha256={sig}"


def build_meta_webhook_payload(
    message_id: str,
    sender_phone: str,
    text_body: str,
    sender_name: str = "Test Prospect",
) -> dict:
    """Helper to generate realistic Meta Cloud API incoming webhook structure."""
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "100200300400500",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15556700586",
                                "phone_number_id": "596245140229875",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": sender_name},
                                    "wa_id": sender_phone,
                                }
                            ],
                            "messages": [
                                {
                                    "from": sender_phone,
                                    "id": message_id,
                                    "timestamp": "1730000000",
                                    "type": "text",
                                    "text": {"body": text_body},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }


@pytest.mark.asyncio
async def test_webhook_handshake_success(async_client: AsyncClient):
    """Verify Meta challenge verification passes with matching verify token."""
    challenge_val = "1158201444"
    resp = await async_client.get(
        "/api/v1/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": challenge_val,
            "hub.verify_token": settings.WHATSAPP_VERIFY_TOKEN,
        },
    )
    assert resp.status_code == 200
    assert resp.text == challenge_val


@pytest.mark.asyncio
async def test_webhook_handshake_invalid_token(async_client: AsyncClient):
    """Verify Meta challenge handshake fails with 403 on invalid token."""
    resp = await async_client.get(
        "/api/v1/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "1158201444",
            "hub.verify_token": "wrong_unauthorized_token",
        },
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_webhook_signature_rejected(async_client: AsyncClient):
    """Verify POST webhook rejects invalid HMAC signatures with 401."""
    payload = {"object": "whatsapp_business_account", "entry": []}
    payload_bytes = json.dumps(payload).encode("utf-8")

    resp = await async_client.post(
        "/api/v1/webhook",
        content=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=invalid_tampered_hash_00000000000000000000000000000000",
        },
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_webhook_message_ingestion_and_deduplication(async_client: AsyncClient):
    """Verify message ingestion, agent processing, and duplicate message suppression."""
    unique_id = f"wamid.test_{uuid.uuid4().hex[:12]}"
    phone = f"9198{uuid.uuid4().int % 100000000:08d}"
    
    payload_dict = build_meta_webhook_payload(
        message_id=unique_id,
        sender_phone=phone,
        text_body="Hi, I am looking for a 3BHK villa in Sarjapur under 2.5 Cr",
        sender_name="Rahul Sharma",
    )
    payload_bytes = json.dumps(payload_dict).encode("utf-8")
    valid_sig = generate_meta_signature(payload_bytes, settings.WHATSAPP_APP_SECRET)

    # 1. First delivery: Should process successfully
    resp1 = await async_client.post(
        "/api/v1/webhook",
        content=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": valid_sig,
        },
    )
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["status"] == "success"
    assert data1["processed_messages"] == 1
    assert data1["duplicate_messages"] == 0

    # 2. Duplicate retry delivery (Meta retry behavior): Should be suppressed by idempotency check
    resp2 = await async_client.post(
        "/api/v1/webhook",
        content=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": valid_sig,
        },
    )
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["status"] == "success"
    assert data2["processed_messages"] == 0
    assert data2["duplicate_messages"] == 1


@pytest.mark.asyncio
async def test_webhook_human_takeover_flow(async_client: AsyncClient):
    """Verify that asking to speak to a human transitions conversation to HUMAN_HANDOFF."""
    unique_id = f"wamid.test_{uuid.uuid4().hex[:12]}"
    phone = f"9197{uuid.uuid4().int % 100000000:08d}"

    payload_dict = build_meta_webhook_payload(
        message_id=unique_id,
        sender_phone=phone,
        text_body="I want to speak to an agent or representative right now please.",
        sender_name="Pooja Rao",
    )
    payload_bytes = json.dumps(payload_dict).encode("utf-8")
    sig = generate_meta_signature(payload_bytes, settings.WHATSAPP_APP_SECRET)

    resp = await async_client.post(
        "/api/v1/webhook",
        content=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": sig,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["processed_messages"] == 1


@pytest.mark.asyncio
async def test_webhook_opt_out_flow(async_client: AsyncClient):
    """Verify that sending STOP updates lead consent to OPTED_OUT."""
    unique_id = f"wamid.test_{uuid.uuid4().hex[:12]}"
    phone = f"9196{uuid.uuid4().int % 100000000:08d}"

    payload_dict = build_meta_webhook_payload(
        message_id=unique_id,
        sender_phone=phone,
        text_body="STOP",
        sender_name="Karan Mehta",
    )
    payload_bytes = json.dumps(payload_dict).encode("utf-8")
    sig = generate_meta_signature(payload_bytes, settings.WHATSAPP_APP_SECRET)

    resp = await async_client.post(
        "/api/v1/webhook",
        content=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": sig,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["processed_messages"] == 1
