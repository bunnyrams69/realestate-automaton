"""
Database Engine and Async Session Management
Provides async SQLAlchemy 2.0 sessions for FastAPI request lifecycles.
"""

from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config.settings import settings
from app.core.logging import logger
from app.db.base import Base

# 1. Async Engine for FastAPI Request Contexts
# When connecting to Supabase PgBouncer (transaction pooling), prepared statements
# must be disabled to prevent "DuplicatePreparedStatementError".
async_engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,      # Automatically verify connection vitality before checkout
    pool_recycle=300,        # Recycle connections every 5 minutes to prevent stale pooler disconnects
    pool_size=10,
    max_overflow=5,
    future=True,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    },
)

# 2. Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevent expired attributes after commits
    autoflush=False,
)

# 3. Synchronous Engine for Migrations and CLI Scripts
sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    future=True,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Dependency: Yields an async database session per request lifecycle.
    Ensures safe transaction rollback on unhandled exceptions and deterministic session close.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initializes database tables by creating metadata schemas if they do not exist.
    """
    async with async_engine.begin() as conn:
        logger.info("Verifying and initializing database schema metadata...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema metadata initialization completed.")
