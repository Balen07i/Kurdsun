# Central Kurdish (Sorani) string table.
# Every tool pulls its user-facing text from here so dialect/translation
# work happens in one place, not scattered across handler files.

STRINGS = {
    # --- Common ---
    "welcome": "👋 بەخێربێیت بۆ بۆتی کوردی!\nئامرازێک هەڵبژێرە:",
    "main_menu_button": "🏠 مینیوی سەرەکی",
    "back_button": "⬅️ گەڕانەوە",
    "cancel_button": "❌ پاشگەزبوونەوە",
    "cancelled": "کردارەکە هەڵوەشێنرایەوە.",
    "unknown_command": "تکایە لە مینیو یەکێک هەڵبژێرە.",
    "rate_limited": "ڕۆژانە تەنها {limit} جار دەتوانیت ئەم ئامرازە بەکاربهێنیت. سبەی دووبارە هەوڵ بدەرەوە 🙏",
    "processing": "⏳ کارەکەت لە پرۆسەدایە، تکایە چاوەڕێ بە...",
    "generic_error": "⚠️ هەڵەیەک ڕوویدا. تکایە دووبارە هەوڵ بدەرەوە.",

    # --- Categories ---
    "cat_media": "📥 میدیا",
    "cat_documents": "📄 بەڵگەنامە",
    "cat_ai": "🤖 ئامرازی زیرەکی دەستکرد",

    # --- TikTok downloader ---
    "tiktok_name": "⬇️ داگرتنی ڤیدیۆی تیکتۆک",
    "tiktok_ask_link": "لینکی ڤیدیۆی تیکتۆکەکەت بنێرە:",
    "tiktok_invalid_link": "ئەمە لینکێکی دروستی تیکتۆک نییە. تکایە لینکێکی ڕاست بنێرە.",
    "tiktok_download_failed": "نەمانتوانی ڤیدیۆکە داگرین. لەوانەیە لینکەکە هەڵە بێت یان ڤیدیۆکە سڕابێتەوە.",
    "tiktok_sending": "✅ ڤیدیۆکە دۆزرایەوە، بۆت دەنێرم...",

    # --- OCR ---
    "ocr_name": "🔎 وێنە بۆ نووسین (OCR)",
    "ocr_ask_image": "وێنەیەک بنێرە تاکو نووسینەکەی بۆ دەقی نووسراو بگۆڕم:",
    "ocr_no_text_found": "هیچ نووسینێک لە وێنەکەدا نەدۆزرایەوە.",
    "ocr_result_header": "📝 دەقی دۆزراوە:",

    # --- Lecture summarizer ---
    "summarizer_name": "📚 کورتکردنەوەی لێکچوون/وانە",
    "summarizer_ask_text": "دەقی وانەکە یان لێکچوونەکەت بنێرە (دەق یان فایلی .txt):",
    "summarizer_too_long": "دەقەکە زۆر درێژە (زیاتر لە {limit} پیت). تکایە کورتی بکەرەوە.",
    "summarizer_failed": "نەمانتوانی کورتکردنەوەکە دروست بکەین. دووبارە هەوڵ بدەرەوە.",
    "summarizer_result_header": "📚 پوختە:",
}


def t(key: str, **kwargs) -> str:
    """Fetch a Kurdish string by key, with optional .format(**kwargs) substitution."""
    text = STRINGS.get(key, key)
    return text.format(**kwargs) if kwargs else text
