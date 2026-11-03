"""
Lead Repository
"""

from typing import Optional, Sequence, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import LeadCategory
from app.models.lead import Lead
from app.repositories.base import BaseRepository
from app.schemas.lead import LeadFilter


class LeadRepository(BaseRepository[Lead]):
    """Data access repository for real estate leads."""

    def __init__(self, session: AsyncSession):
        super().__init__(Lead, session)

    async def get_by_phone(self, phone: str) -> Optional[Lead]:
        """Fetch lead by normalized phone number."""
        stmt = select(Lead).where(Lead.phone == phone)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def filter_leads(self, filters: LeadFilter) -> Tuple[Sequence[Lead], int]:
        """Query leads with filtering and pagination."""
        stmt = select(Lead)
        count_stmt = select(func.count()).select_from(Lead)

        conditions = []
        if filters.lead_category:
            conditions.append(Lead.lead_category == filters.lead_category.value)
        if filters.min_score is not None:
            conditions.append(Lead.lead_score >= filters.min_score)
        if filters.property_type:
            conditions.append(Lead.property_type.ilike(f"%{filters.property_type.strip()}%"))
        if filters.preferred_location:
            conditions.append(Lead.preferred_location.ilike(f"%{filters.preferred_location.strip()}%"))
        if filters.assigned_agent_id:
            conditions.append(Lead.assigned_agent_id == filters.assigned_agent_id)

        if conditions:
            stmt = stmt.where(*conditions)
            count_stmt = count_stmt.where(*conditions)

        skip = (filters.page - 1) * filters.page_size
        stmt = stmt.order_by(Lead.lead_score.desc(), Lead.created_at.desc()).offset(skip).limit(filters.page_size)

        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar_one()

        items_res = await self.session.execute(stmt)
        items = items_res.scalars().all()

        return items, total

    async def update_qualification(
        self,
        lead: Lead,
        score: int,
        category: LeadCategory,
        reasons: list[str],
    ) -> Lead:
        """Update lead score, tier (HOT/WARM/COLD), and audit explanation factors."""
        lead.lead_score = score
        lead.lead_category = category.value
        lead.qualification_reasons = reasons
        await self.session.flush()
        await self.session.refresh(lead)
        return lead
