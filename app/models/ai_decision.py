"""
AI Decision Audit & Observability Model
"""

from typing import Any, Dict, Optional, TYPE_CHECKING
import uuid
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.lead import Lead
    from app.models.conversation import Conversation


class AIDecision(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Explainable record of autonomous classifications, tool calls, and LLM extractions."""
    __tablename__ = "ai_decisions"

    lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    decision_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # LEAD_CLASSIFICATION | PROPERTY_MATCHING | INTENT_DETECTION
    input_context_summary: Mapped[str] = mapped_column(Text, nullable=False)
    output_decision: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    reasoning_summary: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    lead: Mapped[Optional["Lead"]] = relationship("Lead", back_populates="ai_decisions")
    conversation: Mapped[Optional["Conversation"]] = relationship("Conversation", back_populates="ai_decisions")

    __table_args__ = (
        Index("ix_ai_decisions_type_created", "decision_type", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AIDecision id={self.id} type={self.decision_type}>"
