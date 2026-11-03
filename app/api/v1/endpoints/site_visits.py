"""
Site Visit REST Endpoints
Handles appointment scheduling, calendar integration, status tracking, and .ics export.
"""

from datetime import datetime
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import SiteVisitStatus
from app.db.session import get_db_session
from app.integrations.calendar.calendar_service import calendar_service
from app.repositories.property_repository import PropertyRepository
from app.repositories.site_visit_repository import SiteVisitRepository
from app.schemas.site_visit import SiteVisitCreate, SiteVisitResponse, SiteVisitUpdate
from app.services.site_visit_service import SiteVisitService

router = APIRouter(prefix="/site-visits", tags=["Site Visits"])


@router.post("", response_model=SiteVisitResponse, status_code=status.HTTP_201_CREATED)
async def schedule_site_visit(
    payload: SiteVisitCreate,
    session: AsyncSession = Depends(get_db_session),
) -> SiteVisitResponse:
    """Schedule a new property walkthrough appointment."""
    service = SiteVisitService(session)
    return await service.schedule_visit(payload)


@router.get("/{visit_id}", response_model=SiteVisitResponse)
async def get_site_visit(
    visit_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
) -> SiteVisitResponse:
    """Fetch details of a specific site visit appointment."""
    service = SiteVisitService(session)
    return await service.get_visit_by_id(visit_id)


@router.get("/lead/{lead_id}", response_model=List[SiteVisitResponse])
async def list_lead_visits(
    lead_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
) -> List[SiteVisitResponse]:
    """Retrieve all site visits booked for a specific lead."""
    service = SiteVisitService(session)
    return await service.list_visits_for_lead(lead_id)


@router.patch("/{visit_id}/status", response_model=SiteVisitResponse)
async def update_visit_status(
    visit_id: uuid.UUID,
    status_update: SiteVisitStatus = Query(..., description="Target status"),
    notes: str = Query(None, description="Optional status transition notes"),
    session: AsyncSession = Depends(get_db_session),
) -> SiteVisitResponse:
    """Update appointment status (CONFIRMED, RESCHEDULED, COMPLETED, CANCELLED)."""
    service = SiteVisitService(session)
    return await service.update_status(visit_id, status_update, notes)


@router.post("/{visit_id}/reschedule", response_model=SiteVisitResponse)
async def reschedule_site_visit(
    visit_id: uuid.UUID,
    new_time: datetime = Query(..., description="New ISO 8601 visit timestamp"),
    duration_minutes: Optional[int] = Query(None, ge=15, le=180),
    notes: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session),
) -> SiteVisitResponse:
    """Reschedule an existing site visit appointment with conflict detection."""
    service = SiteVisitService(session)
    return await service.reschedule_visit(
        visit_id=visit_id,
        new_time=new_time,
        duration_minutes=duration_minutes,
        notes=notes,
    )


@router.post("/{visit_id}/cancel", response_model=SiteVisitResponse)
async def cancel_site_visit(
    visit_id: uuid.UUID,
    reason: Optional[str] = Query(None, description="Reason for cancellation"),
    session: AsyncSession = Depends(get_db_session),
) -> SiteVisitResponse:
    """Cancel a scheduled site visit and recalculate lead scoring."""
    service = SiteVisitService(session)
    return await service.cancel_visit(visit_id=visit_id, reason=reason)


@router.get("/{visit_id}/calendar.ics")
async def export_calendar_ics(
    visit_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Download universal RFC 5545 .ics iCalendar file for the site visit."""
    visit_repo = SiteVisitRepository(session)
    prop_repo = PropertyRepository(session)

    visit = await visit_repo.get_by_id(visit_id)
    if not visit:
        from app.core.exceptions import EntityNotFoundException
        raise EntityNotFoundException(f"Site visit '{visit_id}' not found")

    prop = await prop_repo.get_by_id(visit.property_id)
    prop_name = prop.name if prop else "Prestige Property"
    prop_loc = prop.location if prop else "Bangalore"

    ics_content = calendar_service.generate_ics_content(
        uid=str(visit.id),
        title=f"Site Visit: {prop_name}",
        start_time=visit.scheduled_time,
        duration_minutes=visit.duration_minutes,
        description=f"Walkthrough appointment for {prop_name}. Notes: {visit.notes or 'None'}",
        location=prop_loc,
    )

    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=site_visit_{visit_id}.ics"},
    )
