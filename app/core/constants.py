"""
Domain Constants and Enumerations
Defines authoritative domain vocabulary for the real estate AI platform.
"""

from enum import Enum


class LeadCategory(str, Enum):
    """Lead qualification tier based on intent, budget, and timeline."""
    HOT = "HOT"       # High intent, defined budget, ready for site visit/purchase
    WARM = "WARM"     # Interested, exploring, needs more details or nurturing
    COLD = "COLD"     # Low intent, out of market, invalid budget, or non-responsive


class PropertyType(str, Enum):
    """Supported real estate property classifications."""
    APARTMENT = "APARTMENT"
    VILLA = "VILLA"
    PLOT = "PLOT"
    PENTHOUSE = "PENTHOUSE"
    COMMERCIAL = "COMMERCIAL"


class PropertyStatus(str, Enum):
    """Property inventory availability status."""
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    SOLD = "SOLD"
    UPCOMING = "UPCOMING"


class ConversationState(str, Enum):
    """State machine states for conversational flows."""
    NEW_ENQUIRY = "NEW_ENQUIRY"
    GREETING = "GREETING"
    REQUIREMENTS_COLLECTION = "REQUIREMENTS_COLLECTION"
    PROPERTY_RECOMMENDATION = "PROPERTY_RECOMMENDATION"
    QUALIFICATION = "QUALIFICATION"
    VISIT_INTEREST = "VISIT_INTEREST"
    VISIT_SCHEDULING = "VISIT_SCHEDULING"
    FOLLOW_UP_PENDING = "FOLLOW_UP_PENDING"
    HUMAN_HANDOFF = "HUMAN_HANDOFF"
    OPTED_OUT = "OPTED_OUT"
    CLOSED = "CLOSED"


class MessageDirection(str, Enum):
    """Direction of WhatsApp communication."""
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class MessageType(str, Enum):
    """Supported message content types."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    DOCUMENT = "document"
    LOCATION = "location"
    TEMPLATE = "template"
    INTERACTIVE = "interactive"


class MessageProcessingStatus(str, Enum):
    """Lifecycle status of an incoming or outgoing message."""
    RECEIVED = "RECEIVED"
    PROCESSED = "PROCESSED"
    QUEUED = "QUEUED"
    SENT = "SENT"
    FAILED = "FAILED"
    DUPLICATE = "DUPLICATE"


class SiteVisitStatus(str, Enum):
    """Lifecycle status of site visit bookings."""
    REQUESTED = "REQUESTED"
    CONFIRMED = "CONFIRMED"
    RESCHEDULED = "RESCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class FollowUpStatus(str, Enum):
    """Lifecycle status of scheduled nurturing tasks."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
