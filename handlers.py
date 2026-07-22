import logging
import uuid

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.core.db.session import create_job, get_or_create_user, get_session
from bot.core.i18n.ku import t
from bot.core.keyboards.main_menu import cancel_keyboard
from bot.core.quota import has_quota_remaining
from bot.tools.tiktok_dl.service import is_valid_tiktok_url

logger = logging.getLogger(__name__)

router = Router(name="tiktok_dl")

TOOL_ID = "tiktok"


class TikTokStates(StatesGroup):
    waiting_for_link = State()


@router.callback_query(F.data == f"tool:{TOOL_ID}")
async def start_tiktok(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TikTokStates.waiting_for_link)
    await callback.message.edit_text(t("tiktok_ask_link"), reply_markup=cancel_keyboard())
    await callback.answer()


@router.message(StateFilter(TikTokStates.waiting_for_link), F.text)
async def receive_tiktok_link(message: Message, state: FSMContext) -> None:
    url = message.text.strip()

    if not is_valid_tiktok_url(url):
        await message.answer(t("tiktok_invalid_link"), reply_markup=cancel_keyboard())
        return

    async with get_session() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.username)
        if not await has_quota_remaining(session, user, TOOL_ID):
            await message.answer(t("rate_limited", limit="N"))
            await state.clear()
            return

        job_id = str(uuid.uuid4())
        await create_job(session, job_id, user.id, message.chat.id, TOOL_ID)

    await state.clear()
    await message.answer(t("processing"))

    # Enqueue the actual download on the Celery worker - keeps the bot responsive.
    from bot.worker.tasks import process_tiktok_download

    process_tiktok_download.delay(job_id=job_id, chat_id=message.chat.id, user_id=user.id, url=url)
