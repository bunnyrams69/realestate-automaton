"""
Integration Tests for Follow-Up Nurturing System
"""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_follow_up_scheduling_and_execution(async_client: AsyncClient):
    # 1. Create a Lead
    phone = f"9194{uuid.uuid4().int % 100000000:08d}"
    lead_payload = {
        "phone": phone,
        "name": "Vikram Sethi",
        "preferred_location": "Whitefield",
        "property_type": "APARTMENT",
        "budget_max": 12000000,
    }
    lead_resp = await async_client.post("/api/v1/leads", json=lead_payload)
    assert lead_resp.status_code == 201
    lead_id = lead_resp.json()["id"]

    # 2. Schedule Follow-up (e.g. attempt 1 with delay 0 for immediate execution)
    schedule_resp = await async_client.post(
        f"/api/v1/follow-ups/schedule/{lead_id}",
        params={"attempt": 1, "delay_hours": 1},
    )
    assert schedule_resp.status_code == 201
    sched_data = schedule_resp.json()
    assert sched_data["status"] == "scheduled"
    assert sched_data["attempt"] == 1

    # 3. Trigger execution of due tasks
    exec_resp = await async_client.post("/api/v1/follow-ups/execute", params={"limit": 25})
    assert exec_resp.status_code == 200
    assert "executed_count" in exec_resp.json()
