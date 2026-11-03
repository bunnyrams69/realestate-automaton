"""
Generic Async Base Repository
Provides standard CRUD methods for SQLAlchemy 2.0 async sessions.
"""

from typing import Any, Generic, List, Optional, Sequence, Type, TypeVar
import uuid
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic asynchronous repository encapsulating standard database persistence operations."""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, entity_id: uuid.UUID) -> Optional[ModelType]:
        """Fetch a single record by primary key UUID."""
        return await self.session.get(self.model, entity_id)

    async def create(self, entity: ModelType) -> ModelType:
        """Add and flush a new record into the session."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: ModelType, update_data: dict[str, Any]) -> ModelType:
        """Apply a dictionary of updates to an existing instance."""
        for field, value in update_data.items():
            if hasattr(entity, field) and value is not None:
                setattr(entity, field, value)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: ModelType) -> None:
        """Delete an entity from the database."""
        await self.session.delete(entity)
        await self.session.flush()

    async def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """List records with pagination."""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self) -> int:
        """Count total records in table."""
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()
