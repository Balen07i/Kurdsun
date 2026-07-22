from __future__ import annotations

import logging
from dataclasses import dataclass

import anthropic

from bot.core.config import settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are an assistant that summarizes lecture or class notes for students. "
    "Produce a clear, well-structured summary with the key points, organized as "
    "short bullet points grouped under headings. If the source text is in "
    "English, reply in clear English. If the source text is in Kurdish, reply "
    "in the same Kurdish dialect as the source. Keep the summary concise and "
    "study-friendly - do not simply restate the whole text."
)


@dataclass
class SummaryResult:
    success: bool
    summary: str | None = None
    error: str | None = None


def summarize(text: str) -> SummaryResult:
    if not settings.anthropic_api_key:
        return SummaryResult(success=False, error="missing_api_key")

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    try:
        response = client.messages.create(
            model=settings.ai_model,
            max_tokens=1200,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": text}],
        )
        summary = "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        ).strip()
        if not summary:
            return SummaryResult(success=False, error="empty_response")
        return SummaryResult(success=True, summary=summary)
    except Exception as exc:
        logger.warning("Lecture summarization failed: %s", exc)
        return SummaryResult(success=False, error=str(exc))
