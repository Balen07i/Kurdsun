from sqlalchemy.ext.asyncio import AsyncSession

from bot.core.config import settings
from bot.core.db.models import User
from bot.core.db.session import count_today_usage


async def has_quota_remaining(session: AsyncSession, user: User, tool_id: str) -> bool:
    """Premium users are unlimited; free users get settings.free_daily_limit per tool per day."""
    if user.is_premium:
        return True
    used_today = await count_today_usage(session, user.id, tool_id)
    return used_today < settings.free_daily_limit
