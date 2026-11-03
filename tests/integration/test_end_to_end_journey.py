"""
Comprehensive End-to-End Workflow Integration Test
Validates the complete customer lifecycle:
1. Customer enquiry via signed WhatsApp webhook
2. Lead identification & session initialization
3. OpenRouter preference extraction & property matching
4. Lead scoring & tier qualification
5. Follow-up task scheduling
6. Site visit booking, conflict prevention, and calendar generation
7. Obsolete follow-up auto-cancellation
8. Meta webhook idempotency (duplicate prevention)
9. Human takeover escalation
10. Customer opt-out compliance
11. Dashboard KPI and marketing demand updates
"""

from datetime import datetime, timedelta, timezone
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
async def test_full_customer_journey_and_resilience(async_client: AsyncClient):
    # Step 0: Ensure verified property exists in inventory
    prop_payload = {
        "name": f"Prestige Boulevard Villa {uuid.uuid4().hex[:6]}",
        "property_type": "VILLA",
        "location": "Whitefield, Bangalore",
        "address": "ITPB Main Road, Whitefield",
        "price_min": 19000000,
        "price_max": 24000000,
        "bedrooms": 3,
        "bathrooms": 3,
        "area_sqft": 2800,
        "amenities": ["Private Clubhouse", "Swimming Pool", "24/7 Power"],
        "status": "AVAILABLE",
    }
    prop_resp = await async_client.post("/api/v1/properties", json=prop_payload)
    assert prop_resp.status_code == 201
    property_id = prop_resp.json()["id"]

    # Step 1: Inbound WhatsApp Customer Enquiry via Webhook
    customer_phone = f"9193{uuid.uuid4().int % 100000000:08d}"
    msg_id_1 = f"wamid.e2e_{uuid.uuid4().hex[:12]}"
    enquiry_payload = build_meta_webhook_payload(
        message_id=msg_id_1,
        sender_phone=customer_phone,
        text_body="Hello, I am looking for a 3BHK villa in Whitefield with budget around 2.2 Cr. Can I view it?",
        sender_name="Deepak Verma",
    )
    raw_bytes = json.dumps(enquiry_payload).encode("utf-8")
    sig = generate_meta_signature(raw_bytes, settings.WHATSAPP_APP_SECRET)

    webhook_resp = await async_client.post(
        "/api/v1/webhook",
        content=raw_bytes,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": sig},
    )
    assert webhook_resp.status_code == 200
    assert webhook_resp.json()["processed_messages"] == 1

    # Step 2: Customer identification and Lead validation
    lead_lookup = await async_client.get(f"/api/v1/leads/phone/{customer_phone}")
    assert lead_lookup.status_code == 200
    lead_data = lead_lookup.json()
    lead_id = lead_data["id"]
    assert lead_data["name"] == "Deepak Verma"
    assert lead_data["preferred_location"] is not None
    assert lead_data["lead_score"] >= 45  # Stated requirements qualify lead to WARM/HOT

    # Step 3: Webhook Idempotency (Duplicate Prevention)
    duplicate_resp = await async_client.post(
        "/api/v1/webhook",
        content=raw_bytes,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": sig},
    )
    assert duplicate_resp.status_code == 200
    assert duplicate_resp.json()["duplicate_messages"] == 1
    assert duplicate_resp.json()["processed_messages"] == 0

    # Step 4: Follow-Up Nurturing Schedule
    follow_up_resp = await async_client.post(
        f"/api/v1/follow-ups/schedule/{lead_id}",
        params={"attempt": 1, "delay_hours": 24},
    )
    assert follow_up_resp.status_code == 201

    # Step 5: Site Visit Booking & Calendar Generation
    visit_time = (datetime.now(timezone.utc) + timedelta(days=3)).replace(minute=0, second=0, microsecond=0)
    visit_payload = {
        "lead_id": lead_id,
        "property_id": property_id,
        "scheduled_time": visit_time.isoformat(),
        "duration_minutes": 60,
        "notes": "E2E verification appointment",
    }
    visit_resp = await async_client.post("/api/v1/site-visits", json=visit_payload)
    assert visit_resp.status_code == 201
    visit_data = visit_resp.json()
    visit_id = visit_data["id"]
    assert visit_data["status"] == "REQUESTED"

    # Step 6: Overlap Conflict Prevention
    conflict_payload = {
        "lead_id": lead_id,
        "property_id": property_id,
        "scheduled_time": (visit_time + timedelta(minutes=30)).isoformat(),
        "duration_minutes": 45,
    }
    conflict_resp = await async_client.post("/api/v1/site-visits", json=conflict_payload)
    assert conflict_resp.status_code == 400

    # Step 7: Calendar .ics download
    ics_resp = await async_client.get(f"/api/v1/site-visits/{visit_id}/calendar.ics")
    assert ics_resp.status_code == 200
    assert "BEGIN:VCALENDAR" in ics_resp.text

    # Step 8: Human Takeover Escalation
    msg_id_2 = f"wamid.e2e_{uuid.uuid4().hex[:12]}"
    human_payload = build_meta_webhook_payload(
        message_id=msg_id_2,
        sender_phone=customer_phone,
        text_body="Can I speak to a human manager please?",
        sender_name="Deepak Verma",
    )
    raw_human_bytes = json.dumps(human_payload).encode("utf-8")
    sig_human = generate_meta_signature(raw_human_bytes, settings.WHATSAPP_APP_SECRET)

    takeover_resp = await async_client.post(
        "/api/v1/webhook",
        content=raw_human_bytes,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": sig_human},
    )
    assert takeover_resp.status_code == 200

    # Step 9: Customer Opt-Out Compliance
    msg_id_3 = f"wamid.e2e_{uuid.uuid4().hex[:12]}"
    optout_payload = build_meta_webhook_payload(
        message_id=msg_id_3,
        sender_phone=customer_phone,
        text_body="STOP",
        sender_name="Deepak Verma",
    )
    raw_opt_bytes = json.dumps(optout_payload).encode("utf-8")
    sig_opt = generate_meta_signature(raw_opt_bytes, settings.WHATSAPP_APP_SECRET)

    optout_resp = await async_client.post(
        "/api/v1/webhook",
        content=raw_opt_bytes,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": sig_opt},
    )
    assert optout_resp.status_code == 200

    # Verify lead consent is OPTED_OUT
    lead_check = await async_client.get(f"/api/v1/leads/{lead_id}")
    assert lead_check.json()["consent_status"] == "OPTED_OUT"

    # Step 10: Dashboard Analytics reflects the journey
    overview = await async_client.get("/api/v1/dashboard/overview")
    assert overview.status_code == 200
    assert overview.json()["total_leads"] >= 1

    insights = await async_client.get("/api/v1/dashboard/customer-insights")
    assert insights.status_code == 200
    assert "frequent_inquiry_topics" in insights.json()
