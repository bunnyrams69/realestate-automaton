"""
Site Visit Repository
Handles data access, interval-overlap conflict detection, and booking queries.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence
import uuid
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import SiteVisitStatus
from app.models.site_visit import SiteVisit
from app.repositories.base import BaseRepository


class SiteVisitRepository(BaseRepository[SiteVisit]):
    """Data access repository for site visit appointments."""

    def __init__(self, session: AsyncSession):
        super().__init__(SiteVisit, session)

    async def get_by_lead(self, lead_id: uuid.UUID) -> Sequence[SiteVisit]:
        stmt = (
            select(SiteVisit)
            .where(SiteVisit.lead_id == lead_id)
            .order_by(SiteVisit.scheduled_time.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def check_interval_conflict(
        self,
        scheduled_time: datetime,
        duration_minutes: int = 45,
        property_id: Optional[uuid.UUID] = None,
        agent_id: Optional[uuid.UUID] = None,
        exclude_visit_id: Optional[uuid.UUID] = None,
    ) -> bool:
        """
        Detects true time-interval overlaps ([start, start + duration])
        against existing REQUESTED or CONFIRMED site visits.
        Checks for:
        1. Double-booking the same property
        2. Double-booking the assigned agent
        """
        # Normalize timezone to UTC
        if scheduled_time.tzinfo is None:
            new_start = scheduled_time.replace(tzinfo=timezone.utc)
        else:
            new_start = scheduled_time.astimezone(timezone.utc)

        new_end = new_start + timedelta(minutes=duration_minutes)

        # Build candidate filter for active appointments within a broad 24h window
        window_start = new_start - timedelta(hours=4)
        window_end = new_end + timedelta(hours=4)

        stmt = select(SiteVisit).where(
            SiteVisit.status.in_([
                SiteVisitStatus.REQUESTED.value,
                SiteVisitStatus.CONFIRMED.value,
            ]),
            SiteVisit.scheduled_time >= window_start,
            SiteVisit.scheduled_time <= window_end,
        )

        if exclude_visit_id:
            stmt = stmt.where(SiteVisit.id != exclude_visit_id)

        resource_conditions = []
        if property_id:
            resource_conditions.append(SiteVisit.property_id == property_id)
        if agent_id:
            resource_conditions.append(SiteVisit.assigned_agent_id == agent_id)

        if resource_conditions:
            stmt = stmt.where(or_(*resource_conditions))

        result = await self.session.execute(stmt)
        candidates = result.scalars().all()

        for cand in candidates:
            cand_start = cand.scheduled_time
            if cand_start.tzinfo is None:
                cand_start = cand_start.replace(tzinfo=timezone.utc)
            else:
                cand_start = cand_start.astimezone(timezone.utc)

            cand_end = cand_start + timedelta(minutes=cand.duration_minutes)

            # Interval overlap condition: (StartA < EndB) and (EndA > StartB)
            if cand_start < new_end and cand_end > new_start:
                return True

        return False

    async def check_conflict(
        self,
        scheduled_time: datetime,
        agent_id: Optional[uuid.UUID] = None,
        property_id: Optional[uuid.UUID] = None,
        duration_minutes: int = 45,
    ) -> bool:
        """Backward-compatible wrapper for interval conflict detection."""
        return await self.check_interval_conflict(
            scheduled_time=scheduled_time,
            duration_minutes=duration_minutes,
            property_id=property_id,
            agent_id=agent_id,
        )
