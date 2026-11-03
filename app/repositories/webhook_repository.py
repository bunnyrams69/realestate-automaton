"""
Webhook Event Repository
Provides idempotency checks and audit logging for incoming webhooks.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.webhook import WebhookEvent
from app.repositories.base import BaseRepository


class WebhookRepository(BaseRepository[WebhookEvent]):
    """Data access repository for webhook event audit and idempotency tracking."""

    def __init__(self, session: AsyncSession):
        super().__init__(WebhookEvent, session)

    async def get_by_event_id(self, event_id: str) -> Optional[WebhookEvent]:
        """Check if an event was already ingested to guarantee deduplication."""
        stmt = select(WebhookEvent).where(WebhookEvent.event_id == event_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def record_event(
        self,
        event_id: str,
        payload: Dict[str, Any],
        provider: str = "whatsapp",
        status: str = "PROCESSING",
    ) -> WebhookEvent:
        """Record an incoming webhook event."""
        event = WebhookEvent(
            event_id=event_id,
            provider=provider,
            status=status,
            payload_json=payload,
            created_at=datetime.now(timezone.utc),
        )
        return await self.create(event)

    async def mark_processed(self, event: WebhookEvent, status: str = "PROCESSED") -> WebhookEvent:
        """Mark event processing completed."""
        event.status = status
        event.processed_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(event)
        return event
