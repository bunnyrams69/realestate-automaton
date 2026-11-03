"""
Lead Management REST Endpoints
"""

from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import LeadCategory
from app.db.session import get_db_session
from app.schemas.common import PaginatedResponse
from app.schemas.lead import (
    LeadCreate,
    LeadFilter,
    LeadResponse,
    LeadUpdate,
)
from app.services.lead_service import LeadService

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.post(
    "",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create or ingest a new lead",
)
async def create_lead(
    payload: LeadCreate,
    session: AsyncSession = Depends(get_db_session),
) -> LeadResponse:
    """Create a new lead and calculate initial qualification score."""
    service = LeadService(session)
    return await service.create_lead(payload)


@router.get(
    "",
    response_model=PaginatedResponse[LeadResponse],
    summary="List leads filtered by category and score",
)
async def list_leads(
    lead_category: Optional[LeadCategory] = Query(None, description="Filter by HOT, WARM, COLD"),
    min_score: Optional[int] = Query(None, ge=0, le=100),
    property_type: Optional[str] = Query(None),
    preferred_location: Optional[str] = Query(None),
    assigned_agent_id: Optional[uuid.UUID] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
) -> PaginatedResponse[LeadResponse]:
    """Retrieve leads with filtering for sales pipeline views."""
    service = LeadService(session)
    filters = LeadFilter(
        lead_category=lead_category,
        min_score=min_score,
        property_type=property_type,
        preferred_location=preferred_location,
        assigned_agent_id=assigned_agent_id,
        page=page,
        page_size=page_size,
    )
    return await service.list_leads(filters)


@router.get(
    "/{lead_id}",
    response_model=LeadResponse,
    summary="Get single lead details",
)
async def get_lead(
    lead_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
) -> LeadResponse:
    """Get lead profile and qualification details by UUID."""
    service = LeadService(session)
    return await service.get_lead_by_id(lead_id)


@router.get(
    "/by-phone/{phone}",
    response_model=LeadResponse,
    summary="Lookup lead by phone number",
)
@router.get(
    "/phone/{phone}",
    response_model=LeadResponse,
    include_in_schema=False,
)
async def get_lead_by_phone(
    phone: str,
    session: AsyncSession = Depends(get_db_session),
) -> LeadResponse:
    """Lookup lead using normalized phone string."""
    service = LeadService(session)
    clean = phone.strip()
    lead = await service.repo.get_by_phone(clean)
    if not lead and clean.startswith("+"):
        lead = await service.repo.get_by_phone(clean.lstrip("+"))
    if not lead and not clean.startswith("+"):
        lead = await service.repo.get_by_phone(f"+{clean}")
    if not lead:
        from app.core.exceptions import EntityNotFoundException
        raise EntityNotFoundException(f"Lead with phone '{phone}' not found")
    return LeadResponse.model_validate(lead)


@router.patch(
    "/{lead_id}",
    response_model=LeadResponse,
    summary="Update lead preferences or status",
)
async def update_lead(
    lead_id: uuid.UUID,
    payload: LeadUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> LeadResponse:
    """Update lead attributes."""
    service = LeadService(session)
    return await service.update_lead(lead_id, payload)


@router.post(
    "/{lead_id}/recalculate-score",
    response_model=LeadResponse,
    summary="Trigger algorithmic qualification re-scoring",
)
async def recalculate_lead_score(
    lead_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
) -> LeadResponse:
    """Recompute lead score (0-100) and assign HOT/WARM/COLD category."""
    service = LeadService(session)
    return await service.recalculate_qualification(lead_id)
