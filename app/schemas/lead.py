"""
Lead Pydantic Schemas
"""

from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.core.constants import LeadCategory


class LeadBase(BaseModel):
    phone: str = Field(..., description="E.164 phone number, e.g. +919876543210")
    name: Optional[str] = Field(None, max_length=255, description="Customer name if discovered")
    preferred_location: Optional[str] = Field(None, max_length=255, description="Target micro-market/area")
    property_type: Optional[str] = Field(None, description="Preferred property classification")
    bedroom_preference: Optional[int] = Field(None, ge=0, le=20, description="Preferred BHK configuration")
    budget_min: Optional[int] = Field(None, ge=0, description="Minimum budget in INR")
    budget_max: Optional[int] = Field(None, ge=0, description="Maximum budget in INR")
    purchase_timeline: Optional[str] = Field(None, description="e.g. Immediate, < 1 month, 3 months")
    financing_status: Optional[str] = Field(None, description="e.g. Pre-approved loan, Self-funded")
    consent_status: str = Field("OPTED_IN", description="WhatsApp consent status")

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        cleaned = "".join(ch for ch in v if ch.isdigit() or ch == "+")
        if not cleaned.startswith("+"):
            cleaned = "+" + cleaned
        if len(cleaned) < 10:
            raise ValueError("Phone number must have at least 10 digits")
        return cleaned


class LeadCreate(LeadBase):
    organization_id: Optional[uuid.UUID] = None
    assigned_agent_id: Optional[uuid.UUID] = None


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    preferred_location: Optional[str] = None
    property_type: Optional[str] = None
    bedroom_preference: Optional[int] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    purchase_timeline: Optional[str] = None
    financing_status: Optional[str] = None
    lead_score: Optional[int] = Field(None, ge=0, le=100)
    lead_category: Optional[LeadCategory] = None
    qualification_reasons: Optional[List[str]] = None
    assigned_agent_id: Optional[uuid.UUID] = None
    consent_status: Optional[str] = None


class LeadQualificationUpdate(BaseModel):
    """Schema for updating lead qualification score and tier from AI evaluation."""
    lead_score: int = Field(..., ge=0, le=100, description="Computed qualification score 0-100")
    lead_category: LeadCategory = Field(..., description="Classification: HOT, WARM, COLD")
    qualification_reasons: List[str] = Field(default_factory=list, description="Audit reasoning factors")


class LeadResponse(LeadBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    lead_score: int = 0
    lead_category: LeadCategory = LeadCategory.COLD
    qualification_reasons: List[str] = []
    assigned_agent_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime


class LeadFilter(BaseModel):
    """Filter parameters for lead pipeline query."""
    lead_category: Optional[LeadCategory] = Field(None, description="Filter by HOT, WARM, COLD")
    min_score: Optional[int] = Field(None, ge=0, le=100)
    property_type: Optional[str] = None
    preferred_location: Optional[str] = None
    assigned_agent_id: Optional[uuid.UUID] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
