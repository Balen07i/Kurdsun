"""
Central configuration. Every secret / environment-specific value lives here
and NOWHERE else in the codebase. Nothing should call os.environ directly
outside this module.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Copy .env.example to .env and fill it in."
        )
    return value


@dataclass(frozen=True)
class Settings:
    bot_token: str = field(default_factory=lambda: _require("BOT_TOKEN"))
    database_url: str = field(default_factory=lambda: _require("DATABASE_URL"))
    redis_url: str = field(default_factory=lambda: os.environ.get("REDIS_URL", "redis://localhost:6379/0"))

    anthropic_api_key: str = field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", ""))
    ai_model: str = field(default_factory=lambda: os.environ.get("AI_MODEL", "claude-sonnet-4-6"))

    log_level: str = field(default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO"))
    tmp_dir: str = field(default_factory=lambda: os.environ.get("TMP_DIR", "./tmp"))
    max_lecture_chars: int = field(default_factory=lambda: int(os.environ.get("MAX_LECTURE_CHARS", "20000")))
    free_daily_limit: int = field(default_factory=lambda: int(os.environ.get("FREE_DAILY_LIMIT", "10")))


settings = Settings()

os.makedirs(settings.tmp_dir, exist_ok=True)
