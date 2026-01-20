"""Throttling middleware to prevent spam."""

import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.config.logging_config import get_logger
from bot.config.settings import settings

logger = get_logger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware to throttle user requests."""

    def __init__(self):
        """Initialize throttling middleware."""
        super().__init__()
        self.throttle_time = settings.throttle_time
        self.user_timestamps: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Throttle user requests.

        Args:
            handler: Handler function
            event: Telegram event
            data: Handler data

        Returns:
            Handler result or None if throttled
        """
        user = data.get("event_from_user")

        if user:
            user_id = user.id
            current_time = time.time()

            # Cleanup old entries periodically to prevent memory leak
            if len(self.user_timestamps) > 10000:
                logger.info(
                    f"Throttling middleware cleanup: {len(self.user_timestamps)} entries before cleanup"
                )
                cutoff = current_time - 3600  # Keep last hour
                self.user_timestamps = {
                    uid: ts for uid, ts in self.user_timestamps.items() if ts > cutoff
                }
                logger.info(
                    f"Throttling middleware cleanup: {len(self.user_timestamps)} entries after cleanup"
                )

            # Check if user is throttled
            last_time = self.user_timestamps.get(user_id, 0)
            time_passed = current_time - last_time

            if time_passed < self.throttle_time:
                # User is throttled, provide feedback
                if hasattr(event, "answer"):
                    await event.answer("⏱ Please wait a moment.")
                return None

            # Update timestamp
            self.user_timestamps[user_id] = current_time

        return await handler(event, data)
