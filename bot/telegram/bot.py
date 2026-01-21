"""Bot and Dispatcher initialization."""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config.logging_config import get_logger
from bot.config.settings import settings
from bot.telegram.middlewares.database import DatabaseMiddleware
from bot.telegram.middlewares.logging import LoggingMiddleware
from bot.telegram.middlewares.throttling import ThrottlingMiddleware
from bot.telegram.middlewares.user_context import UserContextMiddleware

logger = get_logger(__name__)


def create_bot() -> Bot:
    """Create and configure bot instance.

    Returns:
        Configured Bot instance
    """
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    logger.info("Bot instance created")
    return bot


def create_dispatcher() -> Dispatcher:
    """Create and configure dispatcher with middlewares.

    Returns:
        Configured Dispatcher instance
    """
    # Create dispatcher with memory storage
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register middlewares (order matters!)
    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(ThrottlingMiddleware())
    dp.update.middleware(DatabaseMiddleware())
    dp.update.middleware(UserContextMiddleware())

    logger.info("Dispatcher created with middlewares")
    return dp


def setup_handlers(dp: Dispatcher) -> None:
    """Register all handlers.

    Args:
        dp: Dispatcher instance
    """
    # Import handlers here to avoid circular imports
    from bot.telegram.handlers import (
        ai_chat,
        card_management,
        deck_management,
        errors,
        learning,
        start,
        statistics,
        translation,
        unified_message,
    )

    # Register routers
    dp.include_router(start.router)
    dp.include_router(deck_management.router)
    dp.include_router(card_management.router)
    dp.include_router(learning.router)
    dp.include_router(translation.router)  # Callbacks only
    dp.include_router(ai_chat.router)  # Commands only (/translate, /grammar, /clear_history)
    dp.include_router(unified_message.router)  # AI-powered message categorization
    dp.include_router(statistics.router)
    dp.include_router(errors.router)  # Error handler should be last

    logger.info("All handlers registered")
