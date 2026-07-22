"""
Central manifest of every tool in the bot.

To add a new tool later:
  1. Create bot/tools/<your_tool>/{handlers.py, service.py}
  2. Add ONE ToolInfo entry below
  3. Register its router in bot/main.py (one line)

Nothing else needs to change - the main menu, categories, and rate
limiting all read from this registry dynamically.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolInfo:
    id: str            # stable internal id, used in callback_data + DB rows
    name_key: str       # i18n key for display name
    category: str       # groups tools in the main menu
    is_premium: bool = False


CATEGORY_MEDIA = "cat_media"
CATEGORY_DOCUMENTS = "cat_documents"
CATEGORY_AI = "cat_ai"

CATEGORY_ORDER = [CATEGORY_MEDIA, CATEGORY_DOCUMENTS, CATEGORY_AI]

TOOL_REGISTRY: list[ToolInfo] = [
    ToolInfo(id="tiktok", name_key="tiktok_name", category=CATEGORY_MEDIA),
    ToolInfo(id="ocr", name_key="ocr_name", category=CATEGORY_DOCUMENTS),
    ToolInfo(id="summarizer", name_key="summarizer_name", category=CATEGORY_AI),
]


def tools_by_category(category: str) -> list[ToolInfo]:
    return [tool for tool in TOOL_REGISTRY if tool.category == category]


def get_tool(tool_id: str) -> ToolInfo | None:
    return next((tool for tool in TOOL_REGISTRY if tool.id == tool_id), None)
