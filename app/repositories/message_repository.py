"""
Message Repository
"""

from typing import Optional, Sequence
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """Data access repository for individual chat messages."""

    def __init__(self, session: AsyncSession):
        super().__init__(Message, session)

    async def get_by_external_id(self, external_id: str) -> Optional[Message]:
        """Deduplicate incoming messages by Meta wamid."""
        stmt = select(Message).where(Message.external_message_id == external_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_recent_history(
        self,
        conversation_id: uuid.UUID,
        limit: int = 15,
    ) -> Sequence[Message]:
        """Retrieve recent conversation history ordered chronologically for LLM prompt context."""
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        messages = list(result.scalars().all())
        messages.reverse()  # Return in chronological order
        return messages
