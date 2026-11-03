"""
Follow-Up Task ORM Model
"""

from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING
import uuid
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.constants import FollowUpStatus
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.lead import Lead


class FollowUpTask(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Application-owned background nurturing triggers and scheduled re-engagement."""
    __tablename__ = "follow_up_tasks"

    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default=FollowUpStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    task_type: Mapped[str] = mapped_column(String(100), default="nurturing_message", nullable=False)
    payload_json: Mapped[Dict[str, Any]] = mapped_column("payload", JSONB, default=dict, nullable=False)
    claimed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    lead: Mapped["Lead"] = relationship("Lead", back_populates="follow_up_tasks")

    __table_args__ = (
        Index("ix_follow_up_tasks_poll", "status", "scheduled_for"),
        Index("ix_follow_up_tasks_claimed", "status", "claimed_at"),
    )

    def __repr__(self) -> str:
        return f"<FollowUpTask id={self.id} lead={self.lead_id} attempt={self.attempt_number} status={self.status}>"
