"""
Follow-Up Task REST Endpoints
Schedule, list, and execute automated lead nurturing tasks.
"""

from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from app.services.follow_up_service import FollowUpService

router = APIRouter(prefix="/follow-ups", tags=["Follow-Ups"])


@router.post("/schedule/{lead_id}", status_code=status.HTTP_201_CREATED)
async def schedule_follow_up(
    lead_id: uuid.UUID,
    attempt: int = Query(1, ge=1, le=10, description="Follow-up cadence attempt number"),
    delay_hours: Optional[int] = Query(None, ge=1, description="Custom delay override in hours"),
    session: AsyncSession = Depends(get_db_session),
):
    """Schedule the next nurturing touchpoint for a lead."""
    service = FollowUpService(session)
    task = await service.schedule_next_follow_up(
        lead_id=lead_id,
        attempt=attempt,
        custom_delay_hours=delay_hours,
    )
    if not task:
        return {"status": "skipped", "reason": "Max follow-up attempts reached"}
    return {
        "status": "scheduled",
        "task_id": str(task.id),
        "lead_id": str(lead_id),
        "attempt": task.attempt_number,
        "scheduled_for": task.scheduled_for.isoformat(),
    }


@router.post("/execute", status_code=status.HTTP_200_OK)
async def execute_due_follow_ups(
    limit: int = Query(25, ge=1, le=100, description="Max tasks to process in one batch"),
    session: AsyncSession = Depends(get_db_session),
):
    """Poll and dispatch all currently-due follow-up messages."""
    service = FollowUpService(session)
    count = await service.execute_due_tasks(limit=limit)
    return {"status": "completed", "executed_count": count}
