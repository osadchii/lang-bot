"""Language detection utilities for Greek and Russian."""

import re

# Greek Unicode range: U+0370 to U+03FF (Greek and Coptic)
# Extended Greek: U+1F00 to U+1FFF (Greek Extended)
GREEK_PATTERN = re.compile(r"[\u0370-\u03FF\u1F00-\u1FFF]")

# Cyrillic Unicode range: U+0400 to U+04FF
CYRILLIC_PATTERN = re.compile(r"[\u0400-\u04FF]")


def detect_language(text: str) -> str:
    """Detect whether text is Greek or Russian/Cyrillic.

    Args:
        text: Input text

    Returns:
        'greek', 'russian', or 'unknown'
    """
    has_greek = bool(GREEK_PATTERN.search(text))
    has_cyrillic = bool(CYRILLIC_PATTERN.search(text))

    if has_greek and not has_cyrillic:
        return "greek"
    elif has_cyrillic and not has_greek:
        return "russian"
    elif has_greek and has_cyrillic:
        # Mixed text - determine dominant
        greek_count = len(GREEK_PATTERN.findall(text))
        cyrillic_count = len(CYRILLIC_PATTERN.findall(text))
        return "greek" if greek_count >= cyrillic_count else "russian"
    return "unknown"


def is_greek(text: str) -> bool:
    """Check if text contains Greek characters.

    Args:
        text: Input text

    Returns:
        True if text contains Greek characters
    """
    return bool(GREEK_PATTERN.search(text))


def is_russian(text: str) -> bool:
    """Check if text contains Russian/Cyrillic characters.

    Args:
        text: Input text

    Returns:
        True if text contains Russian/Cyrillic characters
    """
    return bool(CYRILLIC_PATTERN.search(text))
