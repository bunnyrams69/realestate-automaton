"""
Integration Tests for Site Visit Scheduling & Calendar Integration
"""

from datetime import datetime, timedelta, timezone
import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_site_visit_lifecycle_and_calendar_export(async_client: AsyncClient):
    # 1. Seed Property
    prop_payload = {
        "name": f"Sobha Palm Court {uuid.uuid4().hex[:6]}",
        "property_type": "APARTMENT",
        "location": "Yelahanka, Bangalore",
        "address": "Doddaballapur Main Road",
        "price_min": 9000000,
        "price_max": 14000000,
        "bedrooms": 3,
        "bathrooms": 3,
        "area_sqft": 1850,
        "amenities": ["Swimming Pool", "Gym", "Tennis Court"],
        "status": "AVAILABLE",
    }
    p_resp = await async_client.post("/api/v1/properties", json=prop_payload)
    assert p_resp.status_code == 201
    property_id = p_resp.json()["id"]

    # 2. Seed Lead
    lead_phone = f"9195{uuid.uuid4().int % 100000000:08d}"
    l_payload = {
        "phone": lead_phone,
        "name": "Ananya Sen",
        "preferred_location": "Yelahanka",
        "property_type": "APARTMENT",
        "budget_max": 15000000,
    }
    l_resp = await async_client.post("/api/v1/leads", json=l_payload)
    assert l_resp.status_code == 201
    lead_id = l_resp.json()["id"]

    # 3. Schedule Site Visit
    visit_time = (datetime.now(timezone.utc) + timedelta(days=2)).replace(minute=0, second=0, microsecond=0)
    visit_payload = {
        "lead_id": lead_id,
        "property_id": property_id,
        "scheduled_time": visit_time.isoformat(),
        "duration_minutes": 60,
        "notes": "Client requested high-floor corner unit inspection.",
    }
    v_resp = await async_client.post("/api/v1/site-visits", json=visit_payload)
    assert v_resp.status_code == 201
    visit_data = v_resp.json()
    visit_id = visit_data["id"]
    assert visit_data["status"] == "REQUESTED"
    assert visit_data["duration_minutes"] == 60

    # 4. Verify Lead was promoted to HOT with enhanced score
    lead_check = await async_client.get(f"/api/v1/leads/{lead_id}")
    assert lead_check.status_code == 200
    updated_lead = lead_check.json()
    assert updated_lead["lead_category"] == "HOT"
    assert updated_lead["lead_score"] >= 75

    # 5. Conflict Check: Booking an overlapping time slot should fail
    # Appointment is 60m from visit_time. Trying to book 30 minutes in should conflict!
    overlapping_time = visit_time + timedelta(minutes=30)
    overlapping_payload = {
        "lead_id": lead_id,
        "property_id": property_id,
        "scheduled_time": overlapping_time.isoformat(),
        "duration_minutes": 45,
    }
    conflict_resp = await async_client.post("/api/v1/site-visits", json=overlapping_payload)
    assert conflict_resp.status_code == 400

    # 6. Fetch Visit by ID
    get_v = await async_client.get(f"/api/v1/site-visits/{visit_id}")
    assert get_v.status_code == 200
    assert get_v.json()["id"] == visit_id

    # 7. Reschedule Visit to next day
    resched_time = visit_time + timedelta(days=1)
    resched_resp = await async_client.post(
        f"/api/v1/site-visits/{visit_id}/reschedule",
        params={"new_time": resched_time.isoformat(), "notes": "Client requested change to Sunday morning"},
    )
    assert resched_resp.status_code == 200
    assert resched_resp.json()["status"] == "RESCHEDULED"

    # 8. Update Status to CONFIRMED
    patch_resp = await async_client.patch(
        f"/api/v1/site-visits/{visit_id}/status",
        params={"status_update": "CONFIRMED", "notes": "Advisor assigned and slot locked."},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "CONFIRMED"

    # 9. Export RFC 5545 iCalendar .ics File
    ics_resp = await async_client.get(f"/api/v1/site-visits/{visit_id}/calendar.ics")
    assert ics_resp.status_code == 200
    assert "BEGIN:VCALENDAR" in ics_resp.text
    assert "BEGIN:VEVENT" in ics_resp.text
    assert "SUMMARY:Site Visit: Sobha Palm Court" in ics_resp.text

    # 10. Cancel Visit
    cancel_resp = await async_client.post(
        f"/api/v1/site-visits/{visit_id}/cancel",
        params={"reason": "Client out of town"},
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"
