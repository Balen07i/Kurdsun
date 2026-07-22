"""
Celery tasks run in a synchronous worker process, but aiogram's Bot is
async-only. Each task spins up a short-lived Bot instance, sends its
result, and tears it down. This keeps the worker fully decoupled from
the main bot process (no shared state, easy to scale workers
independently).
"""
import asyncio
import logging

from aiogram import Bot
from aiogram.types import BufferedInputFile, FSInputFile

from bot.core.config import settings

logger = logging.getLogger(__name__)


async def _send_text(chat_id: int, text: str) -> None:
    bot = Bot(token=settings.bot_token)
    try:
        # Telegram caps messages at 4096 chars - split long results.
        for i in range(0, len(text), 4000):
            await bot.send_message(chat_id, text[i : i + 4000])
    finally:
        await bot.session.close()


async def _send_video_file(chat_id: int, file_path: str, caption: str | None = None) -> None:
    bot = Bot(token=settings.bot_token)
    try:
        await bot.send_video(chat_id, FSInputFile(file_path), caption=caption)
    finally:
        await bot.session.close()


def send_text_result(chat_id: int, text: str) -> None:
    asyncio.run(_send_text(chat_id, text))


def send_video_result(chat_id: int, file_path: str, caption: str | None = None) -> None:
    asyncio.run(_send_video_file(chat_id, file_path, caption))
