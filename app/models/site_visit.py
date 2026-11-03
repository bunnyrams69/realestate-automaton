"""
Site Visit ORM Model
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
import uuid
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.constants import SiteVisitStatus
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.lead import Lead
    from app.models.property import Property
    from app.models.user import User


class SiteVisit(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Scheduled on-site property walkthroughs with calendar synchronization."""
    __tablename__ = "site_visits"

    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    scheduled_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=45, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default=SiteVisitStatus.REQUESTED.value,
        nullable=False,
        index=True,
    )
    google_calendar_event_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    lead: Mapped["Lead"] = relationship("Lead", back_populates="site_visits")
    property: Mapped["Property"] = relationship("Property", back_populates="site_visits")
    assigned_agent: Mapped[Optional["User"]] = relationship("User", back_populates="assigned_site_visits")

    __table_args__ = (
        Index("ix_site_visits_scheduled_status", "scheduled_time", "status"),
    )

    def __repr__(self) -> str:
        return f"<SiteVisit id={self.id} lead={self.lead_id} time={self.scheduled_time} status={self.status}>"
