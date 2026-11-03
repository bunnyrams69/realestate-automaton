"""
API v1 Router Aggregator
Combines all v1 endpoint routers.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import dashboard, follow_ups, health, leads, properties, site_visits, webhook

api_router = APIRouter()

# Health endpoints
api_router.include_router(health.router)

# Core domain endpoints
api_router.include_router(properties.router)
api_router.include_router(leads.router)
api_router.include_router(site_visits.router)
api_router.include_router(follow_ups.router)
api_router.include_router(webhook.router)

# Analytics & observability
api_router.include_router(dashboard.router)
