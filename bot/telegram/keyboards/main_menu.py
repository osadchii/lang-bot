"""Main menu keyboards."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Get main menu keyboard.

    Returns:
        Reply keyboard with main menu options
    """
    builder = ReplyKeyboardBuilder()

    builder.button(text="📚 My Decks")
    builder.button(text="📖 Learn")
    builder.button(text="➕ Add Card")
    builder.button(text="🤖 AI Assistant")
    builder.button(text="📊 Statistics")
    builder.button(text="❓ Help")

    builder.adjust(2, 2, 2)

    return builder.as_markup(resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Get cancel keyboard.

    Returns:
        Reply keyboard with cancel button
    """
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Cancel")
    return builder.as_markup(resize_keyboard=True)


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Get inline keyboard with back to menu button.

    Returns:
        Inline keyboard markup
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Back to Menu", callback_data="main_menu")
    return builder.as_markup()
