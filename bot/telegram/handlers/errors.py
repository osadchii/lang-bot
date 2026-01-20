"""Error handlers."""

from aiogram import Router
from aiogram.types import ErrorEvent

from bot.config.logging_config import get_logger

logger = get_logger(__name__)

router = Router(name="errors")


@router.error()
async def error_handler(event: ErrorEvent):
    """Handle errors in handlers.

    Args:
        event: Error event
    """
    logger.error(f"Error occurred: {event.exception}", exc_info=event.exception)

    # Try to notify user
    if event.update.message:
        try:
            await event.update.message.answer(
                "❌ An error occurred while processing your request.\n"
                "Please try again later or contact support."
            )
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")

    elif event.update.callback_query:
        try:
            await event.update.callback_query.answer(
                "❌ An error occurred. Please try again.",
                show_alert=True,
            )
        except Exception as e:
            logger.error(f"Failed to send error callback to user: {e}")

    return True  # Mark as handled
