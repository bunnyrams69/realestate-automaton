"""
Conversation Session ORM Model
"""

from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
import uuid
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.constants import ConversationState
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.lead import Lead
    from app.models.message import Message
    from app.models.ai_decision import AIDecision


class Conversation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Dialogue session context tracking conversation state and human handoff."""
    __tablename__ = "conversations"

    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel: Mapped[str] = mapped_column(String(50), default="whatsapp", nullable=False)
    state: Mapped[str] = mapped_column(
        String(50),
        default=ConversationState.NEW_ENQUIRY.value,
        nullable=False,
        index=True,
    )
    is_human_takeover: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_message_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    lead: Mapped["Lead"] = relationship("Lead", back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at"
    )
    ai_decisions: Mapped[List["AIDecision"]] = relationship(
        "AIDecision", back_populates="conversation", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_conversations_lead_state", "lead_id", "state"),
    )

    def __repr__(self) -> str:
        return f"<Conversation id={self.id} lead_id={self.lead_id} state={self.state}>"
