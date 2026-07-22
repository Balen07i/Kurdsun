import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

logger = logging.getLogger("bot.updates")


class LoggingMiddleware(BaseMiddleware):
    """Logs every incoming update with the user id, so production issues are traceable."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        user_id = user.id if user else "unknown"

        kind = "update"
        if isinstance(event, Update):
            if event.message:
                kind = f"message:{event.message.content_type}"
            elif event.callback_query:
                kind = f"callback:{event.callback_query.data}"

        logger.info("user=%s %s", user_id, kind)

        try:
            return await handler(event, data)
        except Exception:
            logger.exception("Unhandled error while processing update for user=%s", user_id)
            raise
