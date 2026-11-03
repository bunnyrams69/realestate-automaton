"""
Pydantic Schemas Package
"""

from app.schemas.common import PaginatedResponse, StatusResponse
from app.schemas.conversation import (
    ConversationBase,
    ConversationCreate,
    ConversationResponse,
    MessageBase,
    MessageCreate,
    MessageResponse,
)
from app.schemas.lead import (
    LeadBase,
    LeadCreate,
    LeadFilter,
    LeadQualificationUpdate,
    LeadResponse,
    LeadUpdate,
)
from app.schemas.property import (
    PropertyBase,
    PropertyCreate,
    PropertyFilter,
    PropertyResponse,
    PropertyUpdate,
)
from app.schemas.site_visit import (
    SiteVisitBase,
    SiteVisitCreate,
    SiteVisitResponse,
    SiteVisitUpdate,
)

__all__ = [
    "PaginatedResponse",
    "StatusResponse",
    "PropertyBase",
    "PropertyCreate",
    "PropertyUpdate",
    "PropertyResponse",
    "PropertyFilter",
    "LeadBase",
    "LeadCreate",
    "LeadUpdate",
    "LeadResponse",
    "LeadFilter",
    "LeadQualificationUpdate",
    "ConversationBase",
    "ConversationCreate",
    "ConversationResponse",
    "MessageBase",
    "MessageCreate",
    "MessageResponse",
    "SiteVisitBase",
    "SiteVisitCreate",
    "SiteVisitUpdate",
    "SiteVisitResponse",
]
