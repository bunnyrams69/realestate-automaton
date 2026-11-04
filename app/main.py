"""
FastAPI Application Entrypoint
Initializes middleware, API routes, error handlers, and lifecycle hooks.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.config.settings import settings
from app.core.logging import configure_logging, logger
from app.core.exceptions import AppError, EntityNotFoundError
from app.api.v1.router import api_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle management."""
    configure_logging(level=settings.LOG_LEVEL)
    logger.info(f"Starting {settings.APP_NAME} v{__version__} [{settings.APP_ENV}]")
    logger.info(f"Loaded configuration. Production mode: {settings.is_production}")
    
    # Initialize database metadata schemas
    try:
        await init_db()
    except Exception as exc:
        logger.error(f"Failed to initialize database during startup: {exc}")

    # Launch background follow-up scheduler if not in testing mode
    scheduler_task = None
    if settings.APP_ENV != "testing":
        import asyncio
        from app.jobs.follow_up_runner import follow_up_scheduler
        scheduler_task = asyncio.create_task(follow_up_scheduler(interval_seconds=300))
        logger.info("Background follow-up scheduler initiated.")

    yield

    if scheduler_task:
        scheduler_task.cancel()
        try:
            await scheduler_task
        except Exception:
            pass
        logger.info("Background follow-up scheduler terminated.")

    logger.info("Shutting down application...")


def create_application() -> FastAPI:
    """Builds and configures the FastAPI application instance."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=__version__,
        description="Autonomous AI sales & marketing automation engine for real estate.",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    @app.exception_handler(EntityNotFoundError)
    async def not_found_handler(request: Request, exc: EntityNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "NotFound",
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(AppError)
    async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(f"Handled application exception: {exc.message} (Path: {request.url.path})")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details,
            },
        )

    # Include API Routers
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # Static Assets for WhatsApp Location & Property Media
    import os
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    if os.path.exists("images_lib"):
        app.mount("/static/images", StaticFiles(directory="images_lib"), name="static_images")

    # Privacy Policy page (required by Meta for Live mode)
    @app.get("/privacy-policy", include_in_schema=False)
    async def privacy_policy():
        policy_path = os.path.join("public", "privacy-policy.html")
        if os.path.exists(policy_path):
            return FileResponse(policy_path, media_type="text/html")
        return JSONResponse(content={"message": "Privacy policy"}, status_code=200)

    # Root redirect to Interactive Dashboard Docs
    @app.get("/", include_in_schema=False)
    async def root_redirect():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/docs")

    # Root health probe for Render / load balancers
    @app.get("/health", include_in_schema=False)
    async def root_health():
        return {"status": "healthy", "service": settings.APP_NAME, "version": __version__}

    return app


app = create_application()
