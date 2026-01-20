"""Start and help command handlers."""

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.database.models.user import User
from bot.telegram.keyboards.main_menu import get_main_menu_keyboard

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, user: User, user_created: bool):
    """Handle /start command.

    Args:
        message: Incoming message
        user: User from middleware
        user_created: Whether user was just created
    """
    if user_created:
        welcome_text = (
            f"👋 <b>Welcome to Greek Language Learning Bot, {user.first_name}!</b>\n\n"
            f"I'm here to help you learn Greek using:\n"
            f"• 📚 <b>Spaced Repetition System</b> for optimal learning\n"
            f"• 🤖 <b>AI Assistant</b> for translations and grammar help\n"
            f"• 📊 <b>Progress Tracking</b> to monitor your improvement\n\n"
            f"Get started by creating your first deck or exploring the menu below!"
        )
    else:
        welcome_text = (
            f"👋 <b>Welcome back, {user.first_name}!</b>\n\n"
            f"Ready to continue your Greek learning journey?\n"
            f"Choose an option from the menu below."
        )

    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command.

    Args:
        message: Incoming message
    """
    help_text = (
        "<b>📖 Greek Learning Bot - Help</b>\n\n"
        "<b>Main Features:</b>\n"
        "• <b>📚 My Decks</b> - Manage your flashcard decks\n"
        "• <b>📖 Learn</b> - Start a learning session\n"
        "• <b>➕ Add Card</b> - Create new flashcards\n"
        "• <b>🤖 AI Assistant</b> - Get help with translations and grammar\n"
        "• <b>📊 Statistics</b> - View your learning progress\n\n"
        "<b>Learning System:</b>\n"
        "When reviewing cards, rate your recall:\n"
        "• <b>Again</b> - Forgot completely (card resets)\n"
        "• <b>Hard</b> - Difficult to remember (small interval)\n"
        "• <b>Good</b> - Correct with effort (normal interval)\n"
        "• <b>Easy</b> - Perfect recall (large interval)\n\n"
        "The system automatically schedules cards for optimal learning!\n\n"
        "<b>Commands:</b>\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
    )

    await message.answer(help_text, reply_markup=get_main_menu_keyboard())
