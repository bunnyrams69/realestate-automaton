"""
API v1 Router Aggregator
Combines all v1 endpoint routers.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health

api_router = APIRouter()

# Health endpoints mounted at root of v1 and top-level /health
api_router.include_router(health.router)
