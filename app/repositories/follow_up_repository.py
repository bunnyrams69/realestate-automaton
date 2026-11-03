"""
Follow-Up Task Repository
Handles atomic claiming (SKIP LOCKED), state transitions, retry tracking,
and stale task recovery for scheduled re-engagement nurturing tasks.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.constants import FollowUpStatus
from app.models.follow_up import FollowUpTask
from app.repositories.base import BaseRepository


class FollowUpRepository(BaseRepository[FollowUpTask]):
    """Data access repository for automated nurturing tasks with atomic worker locking."""

    def __init__(self, session: AsyncSession):
        super().__init__(FollowUpTask, session)

    async def claim_due_tasks(
        self,
        as_of: Optional[datetime] = None,
        limit: int = 25,
    ) -> Sequence[FollowUpTask]:
        """
        Atomically claims due tasks using PostgreSQL FOR UPDATE SKIP LOCKED.
        Prevents duplicate execution across multiple uvicorn workers or app instances.
        Immediately transitions claimed rows to PROCESSING status.
        """
        ref_time = as_of or datetime.now(timezone.utc)
        stmt = (
            select(FollowUpTask)
            .where(
                FollowUpTask.status == FollowUpStatus.PENDING.value,
                FollowUpTask.scheduled_for <= ref_time,
            )
            .with_for_update(skip_locked=True)
            .order_by(FollowUpTask.scheduled_for.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        tasks = list(result.scalars().all())

        now_utc = datetime.now(timezone.utc)
        for t in tasks:
            t.status = FollowUpStatus.PROCESSING.value
            t.claimed_at = now_utc

        await self.session.flush()
        return tasks

    async def recover_stale_tasks(self, stale_timeout_minutes: int = 10) -> int:
        """
        Recovers tasks that were claimed by an application instance that crashed or timed out.
        If retry_count < max_retries: resets to PENDING.
        If retry_count >= max_retries: marks FAILED.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=stale_timeout_minutes)
        stmt = (
            select(FollowUpTask)
            .where(
                FollowUpTask.status == FollowUpStatus.PROCESSING.value,
                FollowUpTask.claimed_at <= cutoff,
            )
            .with_for_update(skip_locked=True)
        )
        result = await self.session.execute(stmt)
        stale_tasks = list(result.scalars().all())

        recovered_count = 0
        for t in stale_tasks:
            t.retry_count += 1
            if t.retry_count >= t.max_retries:
                t.status = FollowUpStatus.FAILED.value
                t.last_error = f"Exceeded max retries after crashing in PROCESSING state."
            else:
                t.status = FollowUpStatus.PENDING.value
                t.claimed_at = None
                t.last_error = f"Recovered from dead worker after {stale_timeout_minutes}m timeout."
            recovered_count += 1

        await self.session.flush()
        return recovered_count

    async def cancel_pending_for_lead(self, lead_id: uuid.UUID) -> int:
        """Cancel pending and in-flight tasks when lead opts out or site visit is booked."""
        stmt = select(FollowUpTask).where(
            FollowUpTask.lead_id == lead_id,
            FollowUpTask.status.in_([
                FollowUpStatus.PENDING.value,
                FollowUpStatus.PROCESSING.value,
            ]),
        )
        result = await self.session.execute(stmt)
        tasks = result.scalars().all()
        for t in tasks:
            t.status = FollowUpStatus.CANCELLED.value
        await self.session.flush()
        return len(tasks)

    async def mark_executed(self, task: FollowUpTask) -> FollowUpTask:
        """Mark task as successfully dispatched."""
        task.status = FollowUpStatus.EXECUTED.value
        task.executed_at = datetime.now(timezone.utc)
        task.last_error = None
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def mark_failed(
        self,
        task: FollowUpTask,
        error_msg: str,
        retry_delay_minutes: int = 15,
    ) -> FollowUpTask:
        """
        Tracks failure, records error message, and applies exponential/linear retry
        or marks permanently FAILED when max_retries is reached.
        """
        task.retry_count += 1
        task.last_error = error_msg[:500]

        if task.retry_count < task.max_retries:
            task.status = FollowUpStatus.PENDING.value
            task.claimed_at = None
            task.scheduled_for = datetime.now(timezone.utc) + timedelta(minutes=retry_delay_minutes * task.retry_count)
        else:
            task.status = FollowUpStatus.FAILED.value
            task.executed_at = datetime.now(timezone.utc)

        await self.session.flush()
        await self.session.refresh(task)
        return task
