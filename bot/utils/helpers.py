"""Helper utilities."""

from datetime import datetime, timezone


def get_current_time() -> datetime:
    """Get current UTC time.

    Returns:
        Current datetime in UTC
    """
    return datetime.now(timezone.utc)


def parse_callback_data(callback_data: str) -> dict[str, str]:
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
