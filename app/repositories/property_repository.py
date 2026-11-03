"""
Property Repository
"""

from typing import List, Optional, Sequence, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import PropertyStatus, PropertyType
from app.models.property import Property
from app.repositories.base import BaseRepository
from app.schemas.property import PropertyFilter


class PropertyRepository(BaseRepository[Property]):
    """Data access repository for property listings."""

    def __init__(self, session: AsyncSession):
        super().__init__(Property, session)

    async def filter_properties(self, filters: PropertyFilter) -> Tuple[Sequence[Property], int]:
        """Query properties applying multi-criteria filters and pagination."""
        stmt = select(Property)
        count_stmt = select(func.count()).select_from(Property)

        conditions = []
        if filters.status:
            conditions.append(Property.status == filters.status.value)
        if filters.property_type:
            conditions.append(Property.property_type == filters.property_type.value)
        if filters.location:
            conditions.append(Property.location.ilike(f"%{filters.location.strip()}%"))
        if filters.max_price is not None:
            conditions.append(Property.price_min <= filters.max_price)
        if filters.min_price is not None:
            conditions.append(Property.price_max >= filters.min_price)
        if filters.bedrooms is not None:
            conditions.append(Property.bedrooms == filters.bedrooms)
        if filters.query:
            search = f"%{filters.query.strip()}%"
            conditions.append(or_(Property.name.ilike(search), Property.location.ilike(search)))

        if conditions:
            stmt = stmt.where(*conditions)
            count_stmt = count_stmt.where(*conditions)

        # Pagination
        skip = (filters.page - 1) * filters.page_size
        stmt = stmt.order_by(Property.created_at.desc()).offset(skip).limit(filters.page_size)

        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar_one()

        items_res = await self.session.execute(stmt)
        items = items_res.scalars().all()

        return items, total

    async def match_properties(
        self,
        property_type: Optional[str] = None,
        max_budget: Optional[int] = None,
        location: Optional[str] = None,
        bedrooms: Optional[int] = None,
        limit: int = 3,
    ) -> Sequence[Property]:
        """
        Find best matching available properties for a lead inquiry.
        Runs exact constraint satisfaction first; if fewer than limit results, relaxes budget by +/- 15%.
        """
        # 1. Exact Matching
        stmt = select(Property).where(Property.status == PropertyStatus.AVAILABLE.value)
        conditions = []

        if property_type:
            conditions.append(Property.property_type.ilike(f"%{property_type.strip()}%"))
        if location:
            conditions.append(Property.location.ilike(f"%{location.strip()}%"))
        if bedrooms:
            conditions.append(Property.bedrooms == bedrooms)
        if max_budget:
            conditions.append(Property.price_min <= max_budget)

        if conditions:
            stmt = stmt.where(*conditions)

        stmt = stmt.order_by(Property.price_min.asc()).limit(limit)
        result = await self.session.execute(stmt)
        matches = result.scalars().all()

        # 2. If no exact matches found and budget was provided, relax budget by 15%
        if len(matches) < limit and max_budget:
            relaxed_budget = int(max_budget * 1.15)
            relaxed_stmt = (
                select(Property)
                .where(
                    Property.status == PropertyStatus.AVAILABLE.value,
                    Property.price_min <= relaxed_budget,
                )
            )
            if location:
                relaxed_stmt = relaxed_stmt.where(Property.location.ilike(f"%{location.strip()}%"))
            if property_type:
                relaxed_stmt = relaxed_stmt.where(Property.property_type.ilike(f"%{property_type.strip()}%"))

            relaxed_stmt = relaxed_stmt.order_by(Property.price_min.asc()).limit(limit)
            relaxed_res = await self.session.execute(relaxed_stmt)
            matches = relaxed_res.scalars().all()

        return matches
