"""
Integration Tests for Leads REST API
"""

import time
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_leads_lifecycle_api(async_client: AsyncClient):
    unique_suffix = str(int(time.time()))[-8:]
    phone = f"+9198{unique_suffix}"

    # 1. Create a Hot Lead
    payload = {
        "phone": phone,
        "name": "Ananya Reddy",
        "preferred_location": "Whitefield",
        "property_type": "APARTMENT",
        "bedroom_preference": 3,
        "budget_min": 10000000,
        "budget_max": 14000000,
        "purchase_timeline": "Immediate (ready to buy)",
        "financing_status": "Self-funded",
    }

    create_resp = await async_client.post("/api/v1/leads", json=payload)
    assert create_resp.status_code == 201
    lead_data = create_resp.json()
    lead_id = lead_data["id"]
    assert lead_data["phone"] == phone
    assert lead_data["name"] == "Ananya Reddy"
    # Should be classified as HOT because all criteria are specified
    assert lead_data["lead_score"] >= 75
    assert lead_data["lead_category"] == "HOT"

    # 2. Get lead by ID
    get_resp = await async_client.get(f"/api/v1/leads/{lead_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == lead_id

    # 3. Lookup lead by phone
    lookup_resp = await async_client.get(f"/api/v1/leads/by-phone/{phone}")
    assert lookup_resp.status_code == 200
    assert lookup_resp.json()["id"] == lead_id

    # 4. List leads filtered by category
    list_resp = await async_client.get("/api/v1/leads?lead_category=HOT")
    assert list_resp.status_code == 200
    leads_list = list_resp.json()
    assert leads_list["total"] >= 1
    assert any(item["id"] == lead_id for item in leads_list["items"])

    # 5. Non-existent lead returns 404
    non_existent = "00000000-0000-0000-0000-000000000000"
    not_found_resp = await async_client.get(f"/api/v1/leads/{non_existent}")
    assert not_found_resp.status_code == 404
