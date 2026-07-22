from __future__ import annotations

import logging
from dataclasses import dataclass

import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

# Tesseract language codes: English + Kurdish where available on the host.
# Kurdish (Sorani/Kurmanji) tesseract data isn't always installed by default -
# fall back to English-only if the "kur" traineddata isn't present, so OCR
# still works instead of crashing.
_LANG_PRIMARY = "kur+eng"
_LANG_FALLBACK = "eng"


@dataclass
class OcrResult:
    success: bool
    text: str | None = None
    error: str | None = None


def extract_text(image_path: str) -> OcrResult:
    try:
        image = Image.open(image_path)
    except Exception as exc:
        logger.warning("Failed to open image %s: %s", image_path, exc)
        return OcrResult(success=False, error=str(exc))

    try:
        text = pytesseract.image_to_string(image, lang=_LANG_PRIMARY)
    except pytesseract.TesseractError:
        logger.info("Kurdish OCR language pack unavailable, falling back to English-only")
        try:
            text = pytesseract.image_to_string(image, lang=_LANG_FALLBACK)
        except Exception as exc:
            logger.warning("OCR failed for %s: %s", image_path, exc)
            return OcrResult(success=False, error=str(exc))
    except Exception as exc:
        logger.warning("OCR failed for %s: %s", image_path, exc)
        return OcrResult(success=False, error=str(exc))

    cleaned = text.strip()
    if not cleaned:
        return OcrResult(success=False, error="no_text_found")

    return OcrResult(success=True, text=cleaned)
