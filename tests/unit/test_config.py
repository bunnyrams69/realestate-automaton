"""
Unit Tests for Configuration & Secret Redaction
"""

import logging
from app.config.settings import Settings
from app.core.logging import RedactingFormatter
from app.core.constants import LeadCategory, ConversationState


def test_settings_defaults():
    """Verify default configuration attributes and properties."""
    s = Settings()
    assert s.APP_NAME == "Real Estate AI Sales & Marketing Automation"
    assert s.API_V1_PREFIX == "/api/v1"
    assert isinstance(s.cors_origins, list)
    assert len(s.cors_origins) > 0
    assert s.is_production is False


def test_domain_constants():
    """Verify that domain enums adhere to the canonical domain vocabulary."""
    assert LeadCategory.HOT == "HOT"
    assert LeadCategory.WARM == "WARM"
    assert LeadCategory.COLD == "COLD"
    assert ConversationState.NEW_ENQUIRY == "NEW_ENQUIRY"
    assert ConversationState.HUMAN_HANDOFF == "HUMAN_HANDOFF"


def test_secret_redaction_in_logging():
    """Verify that the RedactingFormatter sanitizes API keys and sensitive tokens."""
    formatter = RedactingFormatter(fmt="%(message)s")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="API Key sk-ant-api03-abcdef123456789 and Bearer token123456789xyz initialized",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    assert "sk-ant-api03-abcdef123456789" not in formatted
    assert "<REDACTED>" in formatted
