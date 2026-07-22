import logging
import uuid

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.core.config import settings
from bot.core.db.session import create_job, get_or_create_user, get_session
from bot.core.i18n.ku import t
from bot.core.keyboards.main_menu import cancel_keyboard
from bot.core.quota import has_quota_remaining

logger = logging.getLogger(__name__)

router = Router(name="lecture_summarizer")

TOOL_ID = "summarizer"


class SummarizerStates(StatesGroup):
    waiting_for_text = State()


@router.callback_query(F.data == f"tool:{TOOL_ID}")
async def start_summarizer(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SummarizerStates.waiting_for_text)
    await callback.message.edit_text(t("summarizer_ask_text"), reply_markup=cancel_keyboard())
    await callback.answer()


async def _enqueue_summary(message: Message, state: FSMContext, text: str) -> None:
    if len(text) > settings.max_lecture_chars:
        await message.answer(t("summarizer_too_long", limit=settings.max_lecture_chars), reply_markup=cancel_keyboard())
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

    from bot.worker.tasks import process_summary

    process_summary.delay(job_id=job_id, chat_id=message.chat.id, user_id=user.id, text=text)


@router.message(StateFilter(SummarizerStates.waiting_for_text), F.text)
async def receive_text(message: Message, state: FSMContext) -> None:
    await _enqueue_summary(message, state, message.text.strip())


@router.message(StateFilter(SummarizerStates.waiting_for_text), F.document)
async def receive_document(message: Message, state: FSMContext) -> None:
    if not message.document.file_name.lower().endswith(".txt"):
        await message.answer(t("summarizer_ask_text"), reply_markup=cancel_keyboard())
        return

    file = await message.bot.get_file(message.document.file_id)
    buffer = await message.bot.download_file(file.file_path)
    text = buffer.read().decode("utf-8", errors="ignore").strip()

    await _enqueue_summary(message, state, text)
