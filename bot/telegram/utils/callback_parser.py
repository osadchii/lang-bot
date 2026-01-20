"""Utilities for safely parsing Telegram callback data."""

from typing import List, Optional


def parse_callback_data(callback_data: str, expected_parts: int) -> Optional[List[str]]:
    """
    Safely parse callback data.

    Args:
        callback_data: The callback data string (e.g., "deck:123")
        expected_parts: Expected number of parts after splitting

    Returns:
        List of parts if valid, None if invalid

    Example:
        >>> parse_callback_data("deck:123", 2)
        ['deck', '123']

        >>> parse_callback_data("invalid", 2)
        None
    """
    parts = callback_data.split(":")
    if len(parts) != expected_parts:
        return None
    return parts


def parse_callback_int(callback_data: str, part_index: int = 1) -> Optional[int]:
    """
    Parse an integer from callback data.

    Args:
        callback_data: The callback data string (e.g., "deck:123")
        part_index: Index of the part to parse as int (default: 1)

    Returns:
        Integer if valid, None if invalid

    Example:
        >>> parse_callback_int("deck:123")
        123

        >>> parse_callback_int("deck:invalid")
        None
    """
    parts = callback_data.split(":")
    if len(parts) <= part_index:
        return None
    try:
        return int(parts[part_index])
    except (ValueError, IndexError):
        return None
