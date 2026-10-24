"""
Health and Status Endpoints
Used for Render / container health checks and platform observability.
"""

from typing import Dict, Any
from fastapi import APIRouter
from app.config.settings import settings
from app import __version__

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Basic service liveness check")
async def health_check() -> Dict[str, Any]:
    """Returns basic liveness status."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": __version__,
        "environment": settings.APP_ENV,
    }


@router.get("/system/status", summary="Detailed system dependency readiness check")
async def system_status() -> Dict[str, Any]:
    """Returns readiness details for key services and integrations."""
    return {
        "status": "operational",
        "app_name": settings.APP_NAME,
        "version": __version__,
        "environment": settings.APP_ENV,
        "integrations": {
            "claude_api": {
                "configured": bool(settings.ANTHROPIC_API_KEY and not settings.ANTHROPIC_API_KEY.startswith("sk-ant-placeholder")),
                "model": settings.CLAUDE_MODEL,
            },
            "whatsapp_cloud_api": {
                "configured": bool(settings.WHATSAPP_API_TOKEN and not settings.WHATSAPP_API_TOKEN.startswith("placeholder")),
                "phone_number_id_configured": bool(settings.WHATSAPP_PHONE_NUMBER_ID and not settings.WHATSAPP_PHONE_NUMBER_ID.startswith("placeholder")),
            },
            "database": {
                "configured": bool(settings.DATABASE_URL),
                "is_supabase": "supabase" in settings.DATABASE_URL.lower(),
            },
            "google_calendar": {
                "configured": bool(settings.GOOGLE_CALENDAR_CREDENTIALS_FILE),
            },
            "meta_marketing": {
                "configured": bool(settings.META_ACCESS_TOKEN),
            },
        },
    }
