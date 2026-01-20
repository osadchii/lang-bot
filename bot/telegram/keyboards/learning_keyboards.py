"""Keyboards for learning sessions."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.core.constants import QUALITY_AGAIN, QUALITY_EASY, QUALITY_GOOD, QUALITY_HARD


def get_show_answer_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard with 'Show Answer' button.

    Returns:
        Inline keyboard with show answer button
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="👁 Show Answer", callback_data="show_answer")
    builder.button(text="❌ End Session", callback_data="end_session")
    builder.adjust(1)
    return builder.as_markup()


def get_quality_rating_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard with quality rating buttons.

    Returns:
        Inline keyboard with quality rating buttons
    """
    builder = InlineKeyboardBuilder()

    builder.button(text="❌ Again", callback_data=f"quality:{QUALITY_AGAIN}")
    builder.button(text="😓 Hard", callback_data=f"quality:{QUALITY_HARD}")
    builder.button(text="✅ Good", callback_data=f"quality:{QUALITY_GOOD}")
    builder.button(text="🎯 Easy", callback_data=f"quality:{QUALITY_EASY}")
    builder.button(text="⏹ End Session", callback_data="end_session")

    builder.adjust(2, 2, 1)

    return builder.as_markup()


def get_deck_selection_keyboard(decks: list) -> InlineKeyboardMarkup:
    """Get keyboard to select a deck for learning.

    Args:
        decks: List of deck instances

    Returns:
        Inline keyboard with deck selection buttons
    """
    builder = InlineKeyboardBuilder()

    for deck in decks:
        builder.button(text=deck.name, callback_data=f"learn:{deck.id}")

    builder.button(text="❌ Cancel", callback_data="main_menu")

    builder.adjust(1)

    return builder.as_markup()


def get_session_end_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard shown at end of learning session.

    Returns:
        Inline keyboard with session end options
    """
    builder = InlineKeyboardBuilder()

    builder.button(text="🔄 Continue Learning", callback_data="continue_learning")
    builder.button(text="📊 View Statistics", callback_data="statistics")
    builder.button(text="🏠 Main Menu", callback_data="main_menu")

    builder.adjust(1)

    return builder.as_markup()
