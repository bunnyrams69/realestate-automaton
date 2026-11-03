"""
Lead ORM Model
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING
import uuid
from sqlalchemy import BigInteger, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.constants import LeadCategory
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.conversation import Conversation
    from app.models.match import LeadPropertyMatch
    from app.models.site_visit import SiteVisit
    from app.models.follow_up import FollowUpTask
    from app.models.ai_decision import AIDecision


class Lead(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Real estate prospect inquiring via WhatsApp or performance marketing."""
    __tablename__ = "leads"

    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    phone: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    preferred_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    property_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bedroom_preference: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    budget_min: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    budget_max: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    purchase_timeline: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    financing_status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    purchase_purpose: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    site_visit_interest: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Qualification & Scoring
    lead_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lead_category: Mapped[str] = mapped_column(
        String(20),
        default=LeadCategory.COLD.value,
        nullable=False,
        index=True,
    )
    qualification_reasons: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    
    assigned_agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    consent_status: Mapped[str] = mapped_column(String(50), default="OPTED_IN", nullable=False)

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="leads")
    assigned_agent: Mapped[Optional["User"]] = relationship("User", back_populates="assigned_leads")
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation", back_populates="lead", cascade="all, delete-orphan"
    )
    property_matches: Mapped[List["LeadPropertyMatch"]] = relationship(
        "LeadPropertyMatch", back_populates="lead", cascade="all, delete-orphan"
    )
    site_visits: Mapped[List["SiteVisit"]] = relationship(
        "SiteVisit", back_populates="lead", cascade="all, delete-orphan"
    )
    follow_up_tasks: Mapped[List["FollowUpTask"]] = relationship(
        "FollowUpTask", back_populates="lead", cascade="all, delete-orphan"
    )
    ai_decisions: Mapped[List["AIDecision"]] = relationship(
        "AIDecision", back_populates="lead", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_leads_category_score", "lead_category", "lead_score"),
    )

    def __repr__(self) -> str:
        return f"<Lead id={self.id} phone='{self.phone}' category={self.lead_category} score={self.lead_score}>"
