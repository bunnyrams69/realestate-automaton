"""
Property Management Service
Encapsulates business rules for catalog inventory management and recommendation filtering.
"""

from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundException, ValidationException
from app.models.property import Property
from app.repositories.property_repository import PropertyRepository
from app.schemas.common import PaginatedResponse
from app.schemas.property import (
    PropertyCreate,
    PropertyFilter,
    PropertyResponse,
    PropertyUpdate,
)


class PropertyService:
    """Service orchestrating property listings and matching."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PropertyRepository(session)

    async def create_property(self, payload: PropertyCreate) -> PropertyResponse:
        """Create a new property listing with validation."""
        if payload.price_max < payload.price_min:
            raise ValidationException("price_max cannot be less than price_min")

        property_entity = Property(
            organization_id=payload.organization_id,
            name=payload.name,
            property_type=payload.property_type.value,
            location=payload.location,
            address=payload.address,
            price_min=payload.price_min,
            price_max=payload.price_max,
            bedrooms=payload.bedrooms,
            bathrooms=payload.bathrooms,
            area_sqft=payload.area_sqft,
            amenities=payload.amenities,
            status=payload.status.value,
            images=payload.images,
            metadata_json=payload.metadata_json,
        )
        saved = await self.repo.create(property_entity)
        return PropertyResponse.model_validate(saved)

    async def get_property_by_id(self, property_id: uuid.UUID) -> PropertyResponse:
        """Retrieve property by ID or raise 404."""
        prop = await self.repo.get_by_id(property_id)
        if not prop:
            raise EntityNotFoundException(f"Property with ID '{property_id}' not found")
        return PropertyResponse.model_validate(prop)

    async def list_properties(self, filters: PropertyFilter) -> PaginatedResponse[PropertyResponse]:
        """List and search properties with pagination."""
        items, total = await self.repo.filter_properties(filters)
        total_pages = (total + filters.page_size - 1) // filters.page_size if total > 0 else 0
        return PaginatedResponse(
            items=[PropertyResponse.model_validate(p) for p in items],
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=total_pages,
        )

    async def update_property(self, property_id: uuid.UUID, payload: PropertyUpdate) -> PropertyResponse:
        """Update property attributes."""
        prop = await self.repo.get_by_id(property_id)
        if not prop:
            raise EntityNotFoundException(f"Property with ID '{property_id}' not found")

        update_dict = payload.model_dump(exclude_unset=True)
        # Convert Enum instances to string values if present
        if "property_type" in update_dict and update_dict["property_type"]:
            update_dict["property_type"] = update_dict["property_type"].value
        if "status" in update_dict and update_dict["status"]:
            update_dict["status"] = update_dict["status"].value

        updated = await self.repo.update(prop, update_dict)
        return PropertyResponse.model_validate(updated)

    async def search_matching(
        self,
        property_type: Optional[str] = None,
        max_budget: Optional[int] = None,
        location: Optional[str] = None,
        bedrooms: Optional[int] = None,
        limit: int = 3,
    ) -> List[PropertyResponse]:
        """Find matching property inventory for lead preferences."""
        matches = await self.repo.match_properties(
            property_type=property_type,
            max_budget=max_budget,
            location=location,
            bedrooms=bedrooms,
            limit=limit,
        )
        return [PropertyResponse.model_validate(p) for p in matches]

    async def match_properties(
        self,
        lead_id: Optional[uuid.UUID] = None,
        property_type: Optional[str] = None,
        location: Optional[str] = None,
        budget_min: Optional[int] = None,
        budget_max: Optional[int] = None,
        bedrooms: Optional[int] = None,
        limit: int = 3,
    ) -> List[PropertyResponse]:
        """Find and rank matching properties against lead preferences."""
        return await self.search_matching(
            property_type=property_type,
            max_budget=budget_max,
            location=location,
            bedrooms=bedrooms,
            limit=limit,
        )
