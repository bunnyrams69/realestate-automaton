"""
Webhook Event Audit & Idempotency Model
"""

from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class WebhookEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Idempotency deduplication and audit store for incoming raw webhooks."""
    __tablename__ = "webhook_events"

    provider: Mapped[str] = mapped_column(String(50), default="whatsapp", nullable=False)
    event_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PROCESSING", nullable=False)
    payload_json: Mapped[Dict[str, Any]] = mapped_column("payload", JSONB, nullable=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_webhook_events_provider_status", "provider", "status"),
    )

    def __repr__(self) -> str:
        return f"<WebhookEvent id={self.id} event_id='{self.event_id}' status='{self.status}'>"
