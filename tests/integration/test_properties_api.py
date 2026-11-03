"""
Integration Tests for Properties REST API
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_properties_crud_api(async_client: AsyncClient):
    # 1. Create a property
    payload = {
        "name": "Greenwood Villa Phase 1",
        "property_type": "VILLA",
        "location": "Sarjapur Road, Bangalore",
        "address": "Survey 42, Sarjapur",
        "price_min": 18000000,
        "price_max": 25000000,
        "bedrooms": 4,
        "bathrooms": 4,
        "area_sqft": 3200,
        "amenities": ["Private Garden", "Clubhouse", "24/7 Security"],
        "status": "AVAILABLE",
        "images": ["https://images.example.com/villa1.jpg"],
        "metadata_json": {"rera_id": "PRM/KA/RERA/1251/308/PR/2026"},
    }

    create_resp = await async_client.post("/api/v1/properties", json=payload)
    assert create_resp.status_code == 201
    created_data = create_resp.json()
    property_id = created_data["id"]
    assert created_data["name"] == payload["name"]
    assert created_data["price_min"] == payload["price_min"]

    # 2. Get the property by ID
    get_resp = await async_client.get(f"/api/v1/properties/{property_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == property_id

    # 3. List properties with filter
    list_resp = await async_client.get("/api/v1/properties?location=Sarjapur")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] >= 1
    assert any(item["id"] == property_id for item in list_data["items"])

    # 4. Search matching properties
    search_resp = await async_client.post(
        "/api/v1/properties/search?max_budget=20000000&location=Sarjapur"
    )
    assert search_resp.status_code == 200
    search_results = search_resp.json()
    assert len(search_results) >= 1

    # 5. Non-existent property returns 404
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    not_found_resp = await async_client.get(f"/api/v1/properties/{non_existent_id}")
    assert not_found_resp.status_code == 404
