"""
Unit Tests for Cal.com Integration Client
Validates date availability fetching, time slot generation, and booking flows.
"""

import pytest
from app.integrations.calcom.client import CalComClient, calcom_client


@pytest.mark.asyncio
async def test_get_available_dates():
    """Verify that available dates returns 5 valid future business dates."""
    dates = await calcom_client.get_available_dates(days_ahead=7)
    assert len(dates) >= 5
    for d in dates:
        assert "date" in d
        assert "display" in d
        assert "day_name" in d


@pytest.mark.asyncio
async def test_get_available_slots():
    """Verify that slot retrieval returns valid slots with formatted strings."""
    dates = await calcom_client.get_available_dates(days_ahead=3)
    target_date = dates[0]["date"]
    slots = await calcom_client.get_available_slots_for_date(target_date)
    assert len(slots) >= 3
    for s in slots:
        assert target_date in s.time
        assert s.formatted_time != ""
        assert s.formatted_date != ""


@pytest.mark.asyncio
async def test_create_booking():
    """Verify that booking creation returns success with valid booking UID."""
    result = await calcom_client.create_booking(
        start_time="2026-11-03T11:30:00+05:30",
        attendee_name="Ganesh",
        attendee_email="ganesh@example.com",
        attendee_phone="+916309913004",
    )
    assert result.success is True
    assert result.booking_uid is not None
    assert result.booking_id is not None
