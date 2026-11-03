"""
Conversation Repository
"""

from datetime import datetime, timezone
from typing import Optional, Sequence
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.constants import ConversationState
from app.models.conversation import Conversation
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """Data access repository for conversation sessions."""

    def __init__(self, session: AsyncSession):
        super().__init__(Conversation, session)

    async def get_active_for_lead(self, lead_id: uuid.UUID) -> Optional[Conversation]:
        """Fetch the current active (non-closed) conversation for a lead, including recent messages."""
        stmt = (
            select(Conversation)
            .where(
                Conversation.lead_id == lead_id,
                Conversation.state != ConversationState.CLOSED.value,
            )
            .options(selectinload(Conversation.messages))
            .order_by(Conversation.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_state(self, conversation: Conversation, new_state: ConversationState) -> Conversation:
        """Transition conversation state machine."""
        conversation.state = new_state.value
        conversation.last_message_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def set_human_takeover(self, conversation: Conversation, is_takeover: bool) -> Conversation:
        """Toggle human agent takeover flag to suppress autonomous replies."""
        conversation.is_human_takeover = is_takeover
        conversation.last_message_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation
