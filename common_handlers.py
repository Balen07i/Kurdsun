import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.core.db.session import get_or_create_user, get_session
from bot.core.i18n.ku import t
from bot.core.keyboards.main_menu import category_menu_keyboard, main_menu_keyboard

logger = logging.getLogger(__name__)

router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    async with get_session() as session:
        await get_or_create_user(session, message.from_user.id, message.from_user.username)
    await message.answer(t("welcome"), reply_markup=main_menu_keyboard())


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(t("welcome"), reply_markup=main_menu_keyboard())


@router.callback_query(F.data == "menu:main")
async def show_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(t("welcome"), reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("cat:"))
async def show_category(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    category = callback.data.split(":", 1)[1]
    await callback.message.edit_text(t(category), reply_markup=category_menu_keyboard(category))
    await callback.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(t("cancelled"), reply_markup=main_menu_keyboard())
