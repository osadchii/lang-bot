"""Translation request detection for Greek-Russian learning."""

import re
from dataclasses import dataclass

from bot.utils.language_detector import detect_language


@dataclass
class TranslationRequest:
    """Represents a detected translation request."""

    word: str
    source_language: str  # 'greek' or 'russian'


# Patterns for translation requests in Russian
TRANSLATION_PATTERNS = [
    # "как переводится X?"
    re.compile(r"^как\s+переводится\s+['\"]?(.+?)['\"]?\s*\??$", re.IGNORECASE),
    # "как перевести X?"
    re.compile(r"^как\s+перевести\s+['\"]?(.+?)['\"]?\s*\??$", re.IGNORECASE),
    # "что значит X?"
    re.compile(r"^что\s+значит\s+['\"]?(.+?)['\"]?\s*\??$", re.IGNORECASE),
    # "что означает X?"
    re.compile(r"^что\s+означает\s+['\"]?(.+?)['\"]?\s*\??$", re.IGNORECASE),
    # "переведи X"
    re.compile(r"^переведи\s+['\"]?(.+?)['\"]?\s*$", re.IGNORECASE),
    # "перевод X"
    re.compile(r"^перевод\s+['\"]?(.+?)['\"]?\s*\??$", re.IGNORECASE),
    # "как будет X по-гречески?"
    re.compile(r"^как\s+будет\s+['\"]?(.+?)['\"]?\s+по[- ]?гречески\s*\??$", re.IGNORECASE),
    # "как по-русски X?"
    re.compile(r"^как\s+по[- ]?русски\s+['\"]?(.+?)['\"]?\s*\??$", re.IGNORECASE),
    # "X по-гречески"
    re.compile(r"^['\"]?(.+?)['\"]?\s+по[- ]?гречески\s*\??$", re.IGNORECASE),
    # "X по-русски"
    re.compile(r"^['\"]?(.+?)['\"]?\s+по[- ]?русски\s*\??$", re.IGNORECASE),
]


def detect_translation_request(text: str) -> TranslationRequest | None:
    """Detect if message is a translation request.

    Detection methods:
    1. Pattern matching: "как переводится X?", "что значит X?", etc.
    2. Single word: If message is a single Greek or Russian word

    Args:
        text: User message

    Returns:
        TranslationRequest if detected, None otherwise
    """
    text = text.strip()

    if not text:
        return None

    # 1. Check patterns
    for pattern in TRANSLATION_PATTERNS:
        if match := pattern.match(text):
            word = match.group(1).strip()
            if word:
                lang = detect_language(word)
                if lang in ("greek", "russian"):
                    return TranslationRequest(word=word, source_language=lang)

    # 2. Single word detection (no spaces, 2-50 characters)
    if " " not in text and 2 <= len(text) <= 50:
        lang = detect_language(text)
        if lang in ("greek", "russian"):
            return TranslationRequest(word=text, source_language=lang)

    return None
