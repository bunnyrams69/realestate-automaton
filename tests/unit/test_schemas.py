"""
Unit Tests for Pydantic Domain Schemas
"""

import pytest
from pydantic import ValidationError
from app.core.constants import LeadCategory, PropertyStatus, PropertyType
from app.schemas.lead import LeadBase, LeadCreate, LeadFilter
from app.schemas.property import PropertyBase, PropertyCreate, PropertyFilter


def test_lead_phone_normalization():
    # Test valid phone formats
    lead = LeadBase(phone="+91 98765 43210")
    assert lead.phone == "+919876543210"

    lead2 = LeadBase(phone="9876543210")
    assert lead2.phone == "+9876543210"

    # Test invalid phone format
    with pytest.raises(ValidationError):
        LeadBase(phone="123")  # too short


def test_property_schema_validation():
    # Valid property
    prop = PropertyCreate(
        name="Prestige Lakeside Habitat",
        property_type=PropertyType.APARTMENT,
        location="Whitefield, Bangalore",
        price_min=8500000,
        price_max=15000000,
        bedrooms=3,
        bathrooms=3,
        area_sqft=1650,
        amenities=["Clubhouse", "Swimming Pool", "Gym"],
        status=PropertyStatus.AVAILABLE,
    )
    assert prop.name == "Prestige Lakeside Habitat"
    assert prop.price_min == 8500000
    assert prop.bedrooms == 3
    assert len(prop.amenities) == 3


def test_property_filter_defaults():
    filt = PropertyFilter()
    assert filt.page == 1
    assert filt.page_size == 20
    assert filt.status == PropertyStatus.AVAILABLE
