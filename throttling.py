"""
Simple Redis-based throttle to stop a single user from hammering a tool
(e.g. spamming the TikTok downloader) and taking down the queue for
everyone else. This is separate from the daily-quota check (which is
per-tool business logic based on usage_logs); this is a short-window
anti-spam guard applied to every callback/message.
"""
import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from redis.asyncio import Redis

from bot.core.config import settings
from bot.core.i18n.ku import t

_redis = Redis.from_url(settings.redis_url, decode_responses=True)

MIN_INTERVAL_SECONDS = 1.5  # minimum gap between actions per user


class ThrottlingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        key = f"throttle:{user.id}"
        now = time.time()
        last = await _redis.get(key)

        if last is not None and now - float(last) < MIN_INTERVAL_SECONDS:
            # Silently drop overly-rapid taps instead of spamming errors back.
            return None

        await _redis.set(key, now, ex=10)
        return await handler(event, data)
