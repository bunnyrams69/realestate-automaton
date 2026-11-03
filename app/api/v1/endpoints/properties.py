"""
Property Inventory REST Endpoints
"""

from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import PropertyStatus, PropertyType
from app.db.session import get_db_session
from app.schemas.common import PaginatedResponse, StatusResponse
from app.schemas.property import (
    PropertyCreate,
    PropertyFilter,
    PropertyResponse,
    PropertyUpdate,
)
from app.services.property_service import PropertyService

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.post(
    "",
    response_model=PropertyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new property listing",
)
async def create_property(
    payload: PropertyCreate,
    session: AsyncSession = Depends(get_db_session),
) -> PropertyResponse:
    """Create a new property listing in the inventory."""
    service = PropertyService(session)
    return await service.create_property(payload)


@router.get(
    "",
    response_model=PaginatedResponse[PropertyResponse],
    summary="List properties with filters and pagination",
)
async def list_properties(
    query: Optional[str] = Query(None, description="Search term for name or location"),
    property_type: Optional[PropertyType] = Query(None),
    location: Optional[str] = Query(None),
    max_price: Optional[int] = Query(None, ge=0),
    min_price: Optional[int] = Query(None, ge=0),
    bedrooms: Optional[int] = Query(None, ge=0),
    status: Optional[PropertyStatus] = Query(PropertyStatus.AVAILABLE),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
) -> PaginatedResponse[PropertyResponse]:
    """Retrieve catalog properties filtered by type, location, price, and bedrooms."""
    service = PropertyService(session)
    filters = PropertyFilter(
        query=query,
        property_type=property_type,
        location=location,
        max_price=max_price,
        min_price=min_price,
        bedrooms=bedrooms,
        status=status,
        page=page,
        page_size=page_size,
    )
    return await service.list_properties(filters)


@router.get(
    "/{property_id}",
    response_model=PropertyResponse,
    summary="Get single property details",
)
async def get_property(
    property_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
) -> PropertyResponse:
    """Get full property details by UUID."""
    service = PropertyService(session)
    return await service.get_property_by_id(property_id)


@router.patch(
    "/{property_id}",
    response_model=PropertyResponse,
    summary="Update property listing",
)
async def update_property(
    property_id: uuid.UUID,
    payload: PropertyUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> PropertyResponse:
    """Update property attributes (e.g., price, status, amenities)."""
    service = PropertyService(session)
    return await service.update_property(property_id, payload)


@router.post(
    "/search",
    response_model=List[PropertyResponse],
    summary="Multi-criteria recommendation match",
)
async def search_matching_properties(
    property_type: Optional[str] = None,
    max_budget: Optional[int] = None,
    location: Optional[str] = None,
    bedrooms: Optional[int] = None,
    limit: int = Query(3, ge=1, le=10),
    session: AsyncSession = Depends(get_db_session),
) -> List[PropertyResponse]:
    """Run recommendation matching for customer preferences."""
    service = PropertyService(session)
    return await service.search_matching(
        property_type=property_type,
        max_budget=max_budget,
        location=location,
        bedrooms=bedrooms,
        limit=limit,
    )
