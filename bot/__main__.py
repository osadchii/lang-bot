"""Entry point for running the bot."""

import asyncio
import sys

from aiogram.types import BotCommand

from bot.config.logging_config import get_logger, setup_logging
from bot.config.settings import settings
from bot.database.engine import close_db
from bot.telegram.bot import create_bot, create_dispatcher, setup_handlers

logger = get_logger(__name__)


async def set_bot_commands(bot):
    """Set bot commands for menu.

    Args:
        bot: Bot instance
    """
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Show help information"),
    ]

    await bot.set_my_commands(commands)
    logger.info("Bot commands set")


async def on_startup():
    """Actions to perform on bot startup."""
    logger.info("Starting Greek Learning Bot...")
    logger.info(f"Debug mode: {settings.debug}")


async def on_shutdown():
    """Actions to perform on bot shutdown."""
    logger.info("Shutting down Greek Learning Bot...")
    await close_db()
    logger.info("Bot stopped")


async def main():
    """Main function to run the bot."""
    # Setup logging
    setup_logging()

    logger.info("=" * 50)
    logger.info("Greek Language Learning Bot")
    logger.info("=" * 50)

    # Create bot and dispatcher
    bot = create_bot()
    dp = create_dispatcher()

    # Setup handlers
    setup_handlers(dp)

    # Set bot commands
    await set_bot_commands(bot)

    # Startup actions
    await on_startup()

    # Delete any existing webhook before polling
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Webhook deleted, pending updates dropped")

    try:
        # Start polling
        logger.info("Starting polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")

    except Exception as e:
        logger.error(f"Error during polling: {e}", exc_info=True)
        sys.exit(1)

    finally:
        # Shutdown actions
        await on_shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
