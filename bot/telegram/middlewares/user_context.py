"""User context middleware."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.types import User as TelegramUser

from bot.services.user_service import UserService


class UserContextMiddleware(BaseMiddleware):
    """Middleware to load or create user and add to handler data."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Load or create user.

        Args:
            handler: Handler function
            event: Telegram event
            data: Handler data

        Returns:
            Handler result
        """
        # Get Telegram user from event
        telegram_user: TelegramUser | None = data.get("event_from_user")

        if telegram_user and "session" in data:
            user_service = UserService(data["session"])

            # Get or create user
            user, created = await user_service.get_or_create_user(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                language_code=telegram_user.language_code,
            )

            data["user"] = user
            data["user_created"] = created

        return await handler(event, data)
