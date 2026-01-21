"""Keyboards for learning sessions."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.core.constants import QUALITY_EASY, QUALITY_FORGOT, QUALITY_REMEMBERED
from bot.messages import common as common_msg
from bot.messages import learning as learn_msg


def get_show_answer_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard with 'Show Answer' button.

    Returns:
        Inline keyboard with show answer button
    """
    builder = InlineKeyboardBuilder()
    builder.button(text=learn_msg.BTN_SHOW_ANSWER, callback_data="show_answer")
    builder.button(text=learn_msg.BTN_END_SESSION, callback_data="end_session")
    builder.adjust(1)
    return builder.as_markup()


def get_quality_rating_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard with quality rating buttons.

    Returns:
        Inline keyboard with quality rating buttons (3-option system)
    """
    builder = InlineKeyboardBuilder()

    builder.button(text=learn_msg.BTN_FORGOT, callback_data=f"quality:{QUALITY_FORGOT}")
    builder.button(text=learn_msg.BTN_REMEMBERED, callback_data=f"quality:{QUALITY_REMEMBERED}")
    builder.button(text=learn_msg.BTN_EASY, callback_data=f"quality:{QUALITY_EASY}")
    builder.button(text=learn_msg.BTN_END_SESSION, callback_data="end_session")

    builder.adjust(3, 1)

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

    builder.button(text=common_msg.BTN_CANCEL, callback_data="main_menu")

    builder.adjust(1)

    return builder.as_markup()


def get_session_end_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard shown at end of learning session.

    Returns:
        Inline keyboard with session end options
    """
    builder = InlineKeyboardBuilder()

    builder.button(text=learn_msg.BTN_CONTINUE_LEARNING, callback_data="continue_learning")
    builder.button(text=learn_msg.BTN_VIEW_STATISTICS, callback_data="statistics")
    builder.button(text=learn_msg.BTN_MAIN_MENU, callback_data="main_menu")

    builder.adjust(1)

    return builder.as_markup()
