"""
Common Pydantic Schemas and Response Wrappers
"""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard pagination wrapper for list endpoints."""
    items: List[T]
    total: int = Field(..., ge=0, description="Total matching records count")
    page: int = Field(1, ge=1, description="Current page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    total_pages: int = Field(..., ge=0, description="Total calculated pages")


class StatusResponse(BaseModel):
    """Standard operation outcome response."""
    status: str = Field("success", description="Status code or flag")
    message: str = Field(..., description="Human-readable outcome description")
    details: Optional[dict] = Field(default=None, description="Additional context or diagnostics")
