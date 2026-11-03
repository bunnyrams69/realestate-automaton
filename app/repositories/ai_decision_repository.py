"""
AI Decision Repository
Provides audit trail and observability for LLM and rule-based decisions.
"""

from typing import Any, Dict, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ai_decision import AIDecision
from app.repositories.base import BaseRepository


class AIDecisionRepository(BaseRepository[AIDecision]):
    """Data access repository for AI decision audit trails."""

    def __init__(self, session: AsyncSession):
        super().__init__(AIDecision, session)

    async def log_decision(
        self,
        decision_type: str,
        input_context_summary: str,
        output_decision: Dict[str, Any],
        reasoning_summary: str,
        lead_id: Optional[uuid.UUID] = None,
        conversation_id: Optional[uuid.UUID] = None,
    ) -> AIDecision:
        """Create and persist an explainable AI decision record."""
        decision = AIDecision(
            decision_type=decision_type,
            input_context_summary=input_context_summary,
            output_decision=output_decision,
            reasoning_summary=reasoning_summary,
            lead_id=lead_id,
            conversation_id=conversation_id,
        )
        return await self.create(decision)
