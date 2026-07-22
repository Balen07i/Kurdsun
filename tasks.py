"""
Every task follows the same shape:
  1. mark job PROCESSING
  2. call the tool's pure service function
  3. on success: send result via Telegram, mark job DONE, log usage
  4. on failure: send a friendly Kurdish error, mark job FAILED, log usage

Keeping that shape identical across tools is what makes adding tool #4
in the queue trivial - copy this pattern, swap the service call.
"""
import asyncio
import logging
import os

from bot.core.db.models import JobStatus
from bot.core.db.session import get_session, log_usage, update_job_status
from bot.core.i18n.ku import t
from bot.worker.celery_app import celery_app
from bot.worker.telegram_sender import send_text_result, send_video_result

logger = logging.getLogger(__name__)


def _run(coro):
    """Run an async DB call from inside a sync Celery task."""
    return asyncio.run(coro)


@celery_app.task(name="tasks.process_tiktok_download", bind=True, max_retries=1)
def process_tiktok_download(self, job_id: str, chat_id: int, user_id: int, url: str) -> None:
    from bot.tools.tiktok_dl.service import download_tiktok

    async def mark(status, error=None):
        async with get_session() as session:
            await update_job_status(session, job_id, status, error)

    _run(mark(JobStatus.PROCESSING))
    result = download_tiktok(url)

    if result.success:
        try:
            send_video_result(chat_id, result.file_path)
            _run(mark(JobStatus.DONE))
            _run(_log(user_id, "tiktok", True))
        finally:
            if result.file_path and os.path.exists(result.file_path):
                os.remove(result.file_path)
    else:
        send_text_result(chat_id, t("tiktok_download_failed"))
        _run(mark(JobStatus.FAILED, result.error))
        _run(_log(user_id, "tiktok", False, "download_failed"))


@celery_app.task(name="tasks.process_ocr", bind=True, max_retries=1)
def process_ocr(self, job_id: str, chat_id: int, user_id: int, image_path: str) -> None:
    from bot.tools.ocr_image.service import extract_text

    async def mark(status, error=None):
        async with get_session() as session:
            await update_job_status(session, job_id, status, error)

    _run(mark(JobStatus.PROCESSING))
    result = extract_text(image_path)

    try:
        if result.success:
            send_text_result(chat_id, f"{t('ocr_result_header')}\n\n{result.text}")
            _run(mark(JobStatus.DONE))
            _run(_log(user_id, "ocr", True))
        else:
            message = t("ocr_no_text_found") if result.error == "no_text_found" else t("generic_error")
            send_text_result(chat_id, message)
            _run(mark(JobStatus.FAILED, result.error))
            _run(_log(user_id, "ocr", False, result.error))
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)


@celery_app.task(name="tasks.process_summary", bind=True, max_retries=1)
def process_summary(self, job_id: str, chat_id: int, user_id: int, text: str) -> None:
    from bot.tools.lecture_summarizer.service import summarize

    async def mark(status, error=None):
        async with get_session() as session:
            await update_job_status(session, job_id, status, error)

    _run(mark(JobStatus.PROCESSING))
    result = summarize(text)

    if result.success:
        send_text_result(chat_id, f"{t('summarizer_result_header')}\n\n{result.summary}")
        _run(mark(JobStatus.DONE))
        _run(_log(user_id, "summarizer", True))
    else:
        send_text_result(chat_id, t("summarizer_failed"))
        _run(mark(JobStatus.FAILED, result.error))
        _run(_log(user_id, "summarizer", False, result.error))


async def _log(user_id: int, tool_id: str, success: bool, error_code: str | None = None) -> None:
    async with get_session() as session:
        await log_usage(session, user_id, tool_id, success, error_code)
