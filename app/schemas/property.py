"""
Property Pydantic Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.core.constants import PropertyStatus, PropertyType


class PropertyBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Project or property title")
    property_type: PropertyType = Field(PropertyType.APARTMENT, description="Property vertical")
    location: str = Field(..., min_length=2, max_length=255, description="Locality or micro-market name")
    address: Optional[str] = Field(None, description="Full physical postal address")
    price_min: int = Field(..., ge=0, description="Minimum price in INR")
    price_max: int = Field(..., ge=0, description="Maximum price in INR")
    bedrooms: Optional[int] = Field(None, ge=0, le=20, description="Number of bedrooms (BHK)")
    bathrooms: Optional[int] = Field(None, ge=0, le=20, description="Number of bathrooms")
    area_sqft: Optional[int] = Field(None, ge=50, description="Super built-up or carpet area in sq ft")
    amenities: List[str] = Field(default_factory=list, description="List of amenities (e.g. Pool, Gym)")
    status: PropertyStatus = Field(PropertyStatus.AVAILABLE, description="Inventory availability status")
    images: List[str] = Field(default_factory=list, description="Array of image URLs / floorplans")
    metadata_json: Dict[str, Any] = Field(default_factory=dict, description="Custom developer attributes")


class PropertyCreate(PropertyBase):
    organization_id: Optional[uuid.UUID] = Field(None, description="Owning organization ID")


class PropertyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    property_type: Optional[PropertyType] = None
    location: Optional[str] = Field(None, min_length=2, max_length=255)
    address: Optional[str] = None
    price_min: Optional[int] = Field(None, ge=0)
    price_max: Optional[int] = Field(None, ge=0)
    bedrooms: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[int] = Field(None, ge=0)
    area_sqft: Optional[int] = Field(None, ge=50)
    amenities: Optional[List[str]] = None
    status: Optional[PropertyStatus] = None
    images: Optional[List[str]] = None
    metadata_json: Optional[Dict[str, Any]] = None


class PropertyResponse(PropertyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime


class PropertyFilter(BaseModel):
    """Multi-criteria property search parameters."""
    query: Optional[str] = Field(None, description="Freeform text match on name/location")
    property_type: Optional[PropertyType] = None
    location: Optional[str] = None
    max_price: Optional[int] = Field(None, ge=0, description="Maximum price filter in INR")
    min_price: Optional[int] = Field(None, ge=0, description="Minimum price filter in INR")
    bedrooms: Optional[int] = Field(None, ge=0)
    status: Optional[PropertyStatus] = Field(PropertyStatus.AVAILABLE)
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
