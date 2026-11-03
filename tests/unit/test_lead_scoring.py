"""
Unit Tests for Lead Qualification Scoring Engine
Tests multi-criteria scoring, boundary thresholds, engagement bonus separation,
explainability breakdowns, and handling of incomplete customer inputs.
"""

import pytest
from app.core.constants import LeadCategory
from app.services.lead_service import LeadService


def test_lead_scoring_complete_hot_prospect():
    """Verify maximum score (100) and HOT tier for a high-intent prospect."""
    score, category, reasons, breakdown = LeadService.compute_qualification_breakdown(
        budget_max=25000000,
        purchase_timeline="Immediate",
        preferred_location="Whitefield, Bangalore",
        property_type="VILLA",
        bedroom_preference=4,
        name="Sunita Narang",
        phone="919876543210",
        has_active_site_visit=False,
    )
    assert score == 100
    assert category == LeadCategory.HOT
    assert breakdown["budget_score"] == 30
    assert breakdown["timeline_score"] == 30
    assert breakdown["preference_score"] == 20
    assert breakdown["identity_score"] == 20
    assert breakdown["engagement_bonus"] == 0
    assert len(reasons) >= 4


def test_lead_scoring_incomplete_cold_prospect():
    """Verify minimum / cold score when only a phone number is provided."""
    score, category, reasons, breakdown = LeadService.compute_qualification_breakdown(
        phone="919876543210",
    )
    assert score == 10
    assert category == LeadCategory.COLD
    assert breakdown["identity_score"] == 10
    assert breakdown["budget_score"] == 0
    assert breakdown["timeline_score"] == 0
    assert breakdown["preference_score"] == 0


def test_lead_scoring_boundary_cold_warm_threshold():
    """Verify exact boundary behavior around WARM threshold (45 points)."""
    # 1. 40 points (budget 30 + phone 10) -> COLD
    score_40, cat_40, _, _ = LeadService.compute_qualification_breakdown(
        budget_max=10000000,
        phone="919876543210",
    )
    assert score_40 == 40
    assert cat_40 == LeadCategory.COLD

    # 2. Exactly 45 points (budget 30 + location 10 + exploratory timeline 5) -> WARM
    score_45, cat_45, _, _ = LeadService.compute_qualification_breakdown(
        budget_max=10000000,
        preferred_location="Indiranagar",
        purchase_timeline="Exploring next year",
    )
    assert score_45 == 45
    assert cat_45 == LeadCategory.WARM


def test_lead_scoring_boundary_warm_hot_threshold():
    """Verify exact boundary behavior around HOT threshold (75 points)."""
    # 1. 70 points -> WARM
    # Budget(30) + Timeline-near(15) + Location(10) + Unit(10) + Phone(10) - wait: 30+15+10+10+10 = 75
    # Let's craft exactly 70: Budget-min(15) + Timeline-immediate(30) + Location(10) + Unit(10) + Phone(10) - wait: 15+30+10+10+10 = 75
    # For 70: Budget(30) + Timeline-near(15) + Location(10) + Name(10) + explore timeline = 5 -> 30+15+10+10+5?
    # Identity is max 20 (Name 10 + Phone 10). Preference is max 20 (Loc 10 + Type 10).
    # Budget(30) + Timeline-near(15) + Preference(20) + Phone(10) -> wait: 30+15+20+10 = 75.
    # What gives 70? Budget(30) + Timeline-near(15) + Location(10) + Phone(10) + explore(5)? Timeline is one string!
    # Let's check: Budget(30) + Timeline-near(15) + Location(10) + Name(10) = 65.
    # If Site Visit added (+20) -> 65 + 20 = 85 (HOT).
    # What about Budget-min(15) + Timeline-near(15) + Preference(20) + Identity(20) = 70.
    score_70, cat_70, _, _ = LeadService.compute_qualification_breakdown(
        budget_min=5000000,
        purchase_timeline="in 2 months",
        preferred_location="Hebbal",
        property_type="APARTMENT",
        name="Arjun Roy",
        phone="919876543210",
    )
    assert score_70 == 70
    assert cat_70 == LeadCategory.WARM

    # 2. Exactly 75 points -> HOT
    score_75, cat_75, _, _ = LeadService.compute_qualification_breakdown(
        budget_max=15000000,           # 30
        purchase_timeline="in 2 months",# 15
        preferred_location="Hebbal",   # 10
        property_type="APARTMENT",     # 10
        phone="919876543210",          # 10
    )
    assert score_75 == 75
    assert cat_75 == LeadCategory.HOT


def test_lead_scoring_engagement_bonus_separation():
    """
    Verify site visit engagement bonus is applied without corrupting
    or mutating the underlying customer purchase timeline.
    """
    # Customer explicitly stated timeline is long-term (e.g. 6 months)
    stated_timeline = "Looking after 6 months"
    score_before, cat_before, _, _ = LeadService.compute_qualification_breakdown(
        budget_max=18000000,
        purchase_timeline=stated_timeline,
        preferred_location="Koramangala",
        phone="919876543210",
        has_active_site_visit=False,
    )
    # Budget(30) + Timeline-long(5) + Location(10) + Phone(10) = 55 (WARM)
    assert score_before == 55
    assert cat_before == LeadCategory.WARM

    # After booking a visit: gets +20 engagement bonus -> 75 (HOT)
    score_after, cat_after, reasons, breakdown = LeadService.compute_qualification_breakdown(
        budget_max=18000000,
        purchase_timeline=stated_timeline,  # Genuine timeline preserved!
        preferred_location="Koramangala",
        phone="919876543210",
        has_active_site_visit=True,
    )
    assert score_after == 75
    assert cat_after == LeadCategory.HOT
    assert breakdown["engagement_bonus"] == 20
    assert "Active site visit appointment scheduled (+20)" in reasons


def test_lead_scoring_clamp_to_100():
    """Verify raw scores exceeding 100 are strictly clamped to 100."""
    score, category, _, breakdown = LeadService.compute_qualification_breakdown(
        budget_max=50000000,            # 30
        purchase_timeline="Immediate",  # 30
        preferred_location="Lavelle Rd",# 10
        property_type="PENTHOUSE",      # 10
        name="Rohan Varma",             # 10
        phone="919876543210",           # 10
        has_active_site_visit=True,     # 20
        # Raw sum = 120
    )
    assert score == 100
    assert breakdown["total_score"] == 100
    assert category == LeadCategory.HOT
