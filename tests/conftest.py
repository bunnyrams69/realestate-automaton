"""
Global Pytest Configuration and Test Fixtures
"""

import os
os.environ["APP_ENV"] = "testing"

import pytest
from httpx import AsyncClient, ASGITransport
from app.config.settings import settings, Settings
settings.APP_ENV = "testing"
from app.main import app


@pytest.fixture
def test_settings() -> Settings:
    """Fixture providing isolated test settings."""
    return Settings(
        APP_NAME="Real Estate AI Test Harness",
        APP_ENV="testing",
        DEBUG=True,
        SECRET_KEY="test-secret-key-for-pytest-execution-only",
        ANTHROPIC_API_KEY="sk-ant-test-key-mock",
        WHATSAPP_VERIFY_TOKEN="test-verify-token",
        WHATSAPP_APP_SECRET="test-app-secret",
    )


@pytest.fixture
async def async_client():
    """Async HTTP client fixture configured with FastAPI ASGI transport."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(autouse=True)
async def cleanup_database_connections():
    """Ensure async engine connections are cleanly disposed between test loops on Windows."""
    yield
    from app.db.session import async_engine
    await async_engine.dispose()

