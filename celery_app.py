from celery import Celery

from bot.core.config import settings
from bot.core.logging_config import setup_logging

setup_logging()

celery_app = Celery(
    "kurdbot",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Heavy tools (media download, AI calls) can take a while - don't let
    # Celery kill them prematurely, but do cap it so a stuck job can't
    # hang forever.
    task_soft_time_limit=180,
    task_time_limit=240,
)

# Import task modules so Celery registers them.
import bot.worker.tasks  # noqa: E402,F401
