"""
Integration Tests for Dashboard & Marketing Analytics
"""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_overview_and_analytics(async_client: AsyncClient):
    # 1. Fetch Overview KPIs
    overview_resp = await async_client.get("/api/v1/dashboard/overview")
    assert overview_resp.status_code == 200
    overview_data = overview_resp.json()
    assert "total_leads" in overview_data
    assert "leads_by_category" in overview_data
    assert "active_conversations" in overview_data
    assert "upcoming_site_visits" in overview_data
    assert "available_properties" in overview_data
    assert "pending_follow_ups" in overview_data

    # 2. Fetch Conversion Funnel
    funnel_resp = await async_client.get("/api/v1/dashboard/conversion-funnel?days=30")
    assert funnel_resp.status_code == 200
    funnel_data = funnel_resp.json()
    assert "funnel" in funnel_data
    assert "rates" in funnel_data
    assert "enquiries" in funnel_data["funnel"]
    assert "qualification_rate" in funnel_data["rates"]

    # 3. Fetch Property Demand Heatmap
    demand_resp = await async_client.get("/api/v1/dashboard/property-demand")
    assert demand_resp.status_code == 200
    demand_data = demand_resp.json()
    assert "top_locations" in demand_data
    assert "top_property_types" in demand_data
    assert "budget_distribution" in demand_data

    # 4. Fetch AI Decision Audit Trail
    decisions_resp = await async_client.get("/api/v1/dashboard/ai-decisions?limit=10")
    assert decisions_resp.status_code == 200
    assert isinstance(decisions_resp.json(), list)

    # 5. Fetch Customer Insights & Objections
    insights_resp = await async_client.get("/api/v1/dashboard/customer-insights?days=30")
    assert insights_resp.status_code == 200
    insights_data = insights_resp.json()
    assert "frequent_inquiry_topics" in insights_data
    assert "top_customer_objections" in insights_data
    assert "site_visit_interest" in insights_data
    assert "meta_advertising_data_status" in insights_data
    assert insights_data["meta_advertising_data_status"]["integrated"] is False
