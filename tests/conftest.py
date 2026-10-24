"""
Global Pytest Configuration and Test Fixtures
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config.settings import Settings


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
