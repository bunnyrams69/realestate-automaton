"""
Background Job Runner
Lightweight asyncio-based scheduler for executing periodic tasks
without external dependencies like Celery or Redis.
"""

import asyncio
from datetime import datetime, timezone
from app.config.settings import settings
from app.core.logging import logger
from app.db.session import AsyncSessionLocal
from app.services.follow_up_service import FollowUpService


async def run_follow_up_job():
    """Execute one cycle of due follow-up tasks."""
    async with AsyncSessionLocal() as session:
        try:
            service = FollowUpService(session)
            count = await service.execute_due_tasks(limit=25)
            if count > 0:
                await session.commit()
                logger.info(f"Follow-up job dispatched {count} nurturing messages.")
        except Exception as e:
            await session.rollback()
            logger.error(f"Follow-up background job error: {e}", exc_info=True)


async def follow_up_scheduler(interval_seconds: int = 300):
    """
    Periodic scheduler that polls for due follow-up tasks.
    Default: every 5 minutes.
    """
    logger.info(f"Follow-up scheduler started. Polling every {interval_seconds}s.")
    while True:
        try:
            await run_follow_up_job()
        except Exception as e:
            logger.error(f"Scheduler loop error: {e}", exc_info=True)
        await asyncio.sleep(interval_seconds)
