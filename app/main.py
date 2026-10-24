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
from app.core.exceptions import AppError
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle management."""
    configure_logging(level=settings.LOG_LEVEL)
    logger.info(f"Starting {settings.APP_NAME} v{__version__} [{settings.APP_ENV}]")
    logger.info(f"Loaded configuration. Production mode: {settings.is_production}")
    yield
    logger.info("Shutting down application...")


def create_application() -> FastAPI:
    """Builds and configures the FastAPI application instance."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=__version__,
        description="Autonomous AI sales & marketing automation engine for real estate.",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json" if not settings.is_production else None,
        docs_url=f"{settings.API_V1_PREFIX}/docs" if not settings.is_production else None,
        redoc_url=f"{settings.API_V1_PREFIX}/redoc" if not settings.is_production else None,
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

    # Global Exception Handler for AppError
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

    # Root health probe for Render / load balancers
    @app.get("/health", include_in_schema=False)
    async def root_health():
        return {"status": "healthy", "service": settings.APP_NAME, "version": __version__}

    return app


app = create_application()
