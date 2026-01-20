"""Logging middleware."""

import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from bot.config.logging_config import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Middleware to log all incoming updates."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Log update processing.

        Args:
            handler: Handler function
            event: Telegram event
            data: Handler data

        Returns:
            Handler result
        """
        start_time = time.time()

        # Get update info
        update: Update = data.get("event_update")
        user = data.get("event_from_user")

        # Log incoming update
        if update and user:
            update_type = update.event_type if hasattr(update, "event_type") else "unknown"
            logger.info(
                f"Update {update.update_id} from user {user.id} ({user.username}): {update_type}"
            )

        try:
            result = await handler(event, data)
            processing_time = time.time() - start_time
            logger.debug(f"Update processed in {processing_time:.2f}s")
            return result

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(
                f"Error processing update after {processing_time:.2f}s: {e}", exc_info=True
            )
            raise
