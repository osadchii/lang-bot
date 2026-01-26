"""Helper utilities."""

import hashlib
from datetime import UTC, datetime


def get_current_time() -> datetime:
    """Get current UTC time.

    Returns:
        Current datetime in UTC
    """
    return datetime.now(UTC)


def parse_callback_data(callback_data: str) -> dict[str, str | list[str]]:
    """Parse callback data string into dictionary.

    Args:
        callback_data: Callback data string (e.g., "action:value:extra")

    Returns:
        Dictionary with parsed data
    """
    parts = callback_data.split(":")
    if len(parts) < 2:
        return {}

    return {"action": parts[0], "value": parts[1], "extra": parts[2:]}


def build_callback_data(action: str, *values) -> str:
    """Build callback data string.

    Args:
        action: Action name
        *values: Values to include

    Returns:
        Callback data string
    """
    return ":".join([action] + [str(v) for v in values])


def create_callback_hash(text: str) -> str:
    """Create a short hash for callback data.

    Used to create unique identifiers for callback data that fit within
    Telegram's callback data size limit (64 bytes).

    Args:
        text: Text to hash

    Returns:
        8-character MD5 hash
    """
    return hashlib.md5(text.encode()).hexdigest()[:8]
