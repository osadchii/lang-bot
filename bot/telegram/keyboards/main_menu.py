"""Main menu keyboards."""

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.messages import common as msg


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Get main menu keyboard.

    Returns:
        Reply keyboard with main menu options
    """
    builder = ReplyKeyboardBuilder()

    builder.button(text=msg.BTN_MY_DECKS)
    builder.button(text=msg.BTN_LEARN)
    builder.button(text=msg.BTN_ADD_CARD)
    builder.button(text=msg.BTN_STATISTICS)

    builder.adjust(2, 2)

    return builder.as_markup(resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Get cancel keyboard.

    Returns:
        Reply keyboard with cancel button
    """
    builder = ReplyKeyboardBuilder()
    builder.button(text=msg.BTN_CANCEL)
    return builder.as_markup(resize_keyboard=True)


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Get inline keyboard with back to menu button.

    Returns:
        Inline keyboard markup
    """
    builder = InlineKeyboardBuilder()
    builder.button(text=msg.BTN_BACK_TO_MENU, callback_data="main_menu")
    return builder.as_markup()
