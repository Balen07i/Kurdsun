import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from bot.core import common_handlers
from bot.core.config import settings
from bot.core.logging_config import setup_logging
from bot.core.middleware.logging_middleware import LoggingMiddleware
from bot.core.middleware.throttling import ThrottlingMiddleware

# --- Tool routers ---
# Adding a new tool = one import + one include_router call below.
from bot.tools.tiktok_dl import handlers as tiktok_handlers
from bot.tools.ocr_image import handlers as ocr_handlers
from bot.tools.lecture_summarizer import handlers as summarizer_handlers

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging()
    logger.info("Starting Kurdish Utility Bot...")

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = RedisStorage.from_url(settings.redis_url)
    dp = Dispatcher(storage=storage)

    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(ThrottlingMiddleware())

    dp.include_router(common_handlers.router)
    dp.include_router(tiktok_handlers.router)
    dp.include_router(ocr_handlers.router)
    dp.include_router(summarizer_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
