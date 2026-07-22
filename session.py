from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.core.config import settings
from bot.core.db.models import Job, JobStatus, UsageLog, User

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_session():
    async with SessionLocal() as session:
        yield session


async def get_or_create_user(session: AsyncSession, telegram_id: int, username: str | None) -> User:
    user = await session.get(User, telegram_id)
    if user is None:
        user = User(id=telegram_id, username=username)
        session.add(user)
        await session.commit()
        logger.info("Created new user %s", telegram_id)
    return user


async def log_usage(session: AsyncSession, user_id: int, tool_id: str, success: bool, error_code: str | None = None) -> None:
    session.add(UsageLog(user_id=user_id, tool_id=tool_id, success=success, error_code=error_code))
    await session.commit()


async def count_today_usage(session: AsyncSession, user_id: int, tool_id: str) -> int:
    since = datetime.now(timezone.utc) - timedelta(days=1)
    result = await session.execute(
        select(func.count(UsageLog.id)).where(
            UsageLog.user_id == user_id,
            UsageLog.tool_id == tool_id,
            UsageLog.created_at >= since,
        )
    )
    return result.scalar_one()


async def create_job(session: AsyncSession, job_id: str, user_id: int, chat_id: int, tool_id: str) -> Job:
    job = Job(id=job_id, user_id=user_id, chat_id=chat_id, tool_id=tool_id, status=JobStatus.PENDING)
    session.add(job)
    await session.commit()
    return job


async def update_job_status(session: AsyncSession, job_id: str, status: JobStatus, error_message: str | None = None) -> None:
    job = await session.get(Job, job_id)
    if job is None:
        logger.warning("update_job_status: job %s not found", job_id)
        return
    job.status = status
    job.error_message = error_message
    if status in (JobStatus.DONE, JobStatus.FAILED):
        job.finished_at = datetime.now(timezone.utc)
    await session.commit()
