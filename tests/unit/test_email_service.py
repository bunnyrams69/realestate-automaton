"""
Unit Tests for Email Confirmation Service
Validates HTML generation, branding placeholders, and recipient dispatch checks.
"""

import pytest
from app.services.email_service import email_service


def test_build_booking_email_html():
    """Verify that email HTML contains all required customer and consultant fields."""
    html = email_service.build_booking_email_html(
        customer_name="Ganesh",
        property_name="Prestige High Fields",
        location="Gachibowli",
        scheduled_date_str="Monday, Nov 3",
        scheduled_time_str="11:30 AM",
        booking_ref="CAL-SITE-VISIT-001",
    )
    assert "Prestige Realty" in html
    assert "Ganesh" in html
    assert "Prestige High Fields" in html
    assert "Gachibowli" in html
    assert "Monday, Nov 3" in html
    assert "11:30 AM" in html
    assert "CAL-SITE-VISIT-001" in html


@pytest.mark.asyncio
async def test_send_booking_confirmation_valid():
    """Verify dispatch returns True for valid email."""
    result = await email_service.send_booking_confirmation(
        to_email="test.client@example.com",
        customer_name="Test Customer",
        property_name="Prestige Park Grove",
        location="Whitefield",
        scheduled_date_str="Wednesday, Nov 5",
        scheduled_time_str="2:00 PM",
        booking_ref="REF-12345",
    )
    assert result is True


@pytest.mark.asyncio
async def test_send_booking_confirmation_invalid_email():
    """Verify dispatch skips gracefully on malformed email."""
    result = await email_service.send_booking_confirmation(
        to_email="invalid-email-string",
        customer_name="Test Customer",
        property_name="Prestige Park Grove",
        location="Whitefield",
        scheduled_date_str="Wednesday, Nov 5",
        scheduled_time_str="2:00 PM",
        booking_ref="REF-12345",
    )
    assert result is False
