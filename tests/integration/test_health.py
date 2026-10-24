"""
Integration Tests for Health and System Status Endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_health_endpoint(async_client: AsyncClient):
    """Verify that root /health responds with 200 and healthy status."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_api_v1_health_endpoint(async_client: AsyncClient):
    """Verify that /api/v1/health responds with 200 and structured metadata."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["environment"] in ["development", "testing", "production"]


@pytest.mark.asyncio
async def test_api_v1_system_status_endpoint(async_client: AsyncClient):
    """Verify that /api/v1/system/status responds with dependency readiness details."""
    response = await async_client.get("/api/v1/system/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "integrations" in data
    assert "claude_api" in data["integrations"]
    assert "whatsapp_cloud_api" in data["integrations"]
    assert "database" in data["integrations"]
