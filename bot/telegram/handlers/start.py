"""Start and help command handlers."""

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.database.models.user import User
from bot.messages import start as start_msg
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
    welcome_text = start_msg.get_welcome_message(user.first_name, user_created)
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command.

    Args:
        message: Incoming message
    """
    await message.answer(start_msg.HELP_TEXT, reply_markup=get_main_menu_keyboard())
