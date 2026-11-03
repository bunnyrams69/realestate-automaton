"""
Site Visit Pydantic Schemas
"""

from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.core.constants import SiteVisitStatus


class SiteVisitBase(BaseModel):
    lead_id: uuid.UUID
    property_id: uuid.UUID
    assigned_agent_id: Optional[uuid.UUID] = None
    scheduled_time: datetime = Field(..., description="ISO 8601 scheduled visit timestamp")
    duration_minutes: int = Field(45, ge=15, le=180)
    status: SiteVisitStatus = Field(SiteVisitStatus.REQUESTED)
    notes: Optional[str] = None


class SiteVisitCreate(SiteVisitBase):
    pass


class SiteVisitUpdate(BaseModel):
    scheduled_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: Optional[SiteVisitStatus] = None
    google_calendar_event_id: Optional[str] = None
    notes: Optional[str] = None
    assigned_agent_id: Optional[uuid.UUID] = None


class SiteVisitResponse(SiteVisitBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    google_calendar_event_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
