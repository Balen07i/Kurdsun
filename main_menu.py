from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.core.i18n.ku import t
from bot.tools.registry import CATEGORY_ORDER, tools_by_category


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Top-level menu: one button per category, built from CATEGORY_ORDER."""
    rows = [
        [InlineKeyboardButton(text=t(category), callback_data=f"cat:{category}")]
        for category in CATEGORY_ORDER
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def category_menu_keyboard(category: str) -> InlineKeyboardMarkup:
    """Sub-menu: one button per tool in that category, plus a back button."""
    rows = [
        [InlineKeyboardButton(text=t(tool.name_key), callback_data=f"tool:{tool.id}")]
        for tool in tools_by_category(category)
    ]
    rows.append([InlineKeyboardButton(text=t("main_menu_button"), callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t("main_menu_button"), callback_data="menu:main")]]
    )


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t("cancel_button"), callback_data="menu:main")]]
    )
