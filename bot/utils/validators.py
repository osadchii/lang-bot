"""Validation utilities."""

import re


def is_valid_deck_name(name: str) -> bool:
    """Validate deck name.

    Args:
        name: Deck name to validate

    Returns:
        True if valid
    """
    if not name or len(name) < 1:
        return False

    if len(name) > 100:
        return False

    return True


def is_valid_card_text(text: str) -> bool:
    """Validate card text (front or back).

    Args:
        text: Card text to validate

    Returns:
        True if valid
    """
    if not text or len(text) < 1:
        return False

    if len(text) > 1000:
        return False

    return True


def contains_greek_characters(text: str) -> bool:
    """Check if text contains Greek characters.

    Args:
        text: Text to check

    Returns:
        True if contains Greek characters
    """
    greek_pattern = re.compile(r"[\u0370-\u03FF\u1F00-\u1FFF]")
    return bool(greek_pattern.search(text))


def is_valid_example(text: str) -> bool:
    """Validate example sentence.

    Args:
        text: Example text to validate

    Returns:
        True if valid
    """
    if not text:
        return True  # Example is optional

    if len(text) > 2000:
        return False

    return True
