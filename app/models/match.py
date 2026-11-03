"""
Lead Property Match ORM Model
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import DateTime, ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.lead import Lead
    from app.models.property import Property


class LeadPropertyMatch(Base, UUIDPrimaryKeyMixin):
    """Auditable record of properties matched to a lead by the AI recommendation engine."""
    __tablename__ = "lead_property_matches"

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
    match_score: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    lead: Mapped["Lead"] = relationship("Lead", back_populates="property_matches")
    property: Mapped["Property"] = relationship("Property", back_populates="lead_matches")

    __table_args__ = (
        Index("ix_matches_lead_score", "lead_id", "match_score"),
    )

    def __repr__(self) -> str:
        return f"<LeadPropertyMatch lead={self.lead_id} property={self.property_id} score={self.match_score}>"
