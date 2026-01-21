"""Keyboards for deck management."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models.deck import Deck
from bot.messages import common as common_msg
from bot.messages import decks as deck_msg


def get_deck_list_keyboard(decks: list[Deck]) -> InlineKeyboardMarkup:
    """Get keyboard with list of decks.

    Args:
        decks: List of deck instances

    Returns:
        Inline keyboard with deck buttons
    """
    builder = InlineKeyboardBuilder()

    for deck in decks:
        builder.button(text=deck.name, callback_data=f"deck:{deck.id}")

    builder.button(text=deck_msg.BTN_CREATE_DECK, callback_data="deck:create")
    builder.button(text=common_msg.BTN_BACK_TO_MENU, callback_data="main_menu")

    builder.adjust(1)

    return builder.as_markup()


def get_deck_actions_keyboard(deck_id: int) -> InlineKeyboardMarkup:
    """Get keyboard with deck actions.

    Args:
        deck_id: Deck ID

    Returns:
        Inline keyboard with deck action buttons
    """
    builder = InlineKeyboardBuilder()

    builder.button(text=deck_msg.BTN_START_LEARNING, callback_data=f"learn:{deck_id}")
    builder.button(text=deck_msg.BTN_ADD_CARD_TO_DECK, callback_data=f"add_card:{deck_id}")
    builder.button(text=deck_msg.BTN_VIEW_CARDS, callback_data=f"view_cards:{deck_id}")
    builder.button(text=deck_msg.BTN_EDIT_DECK, callback_data=f"edit_deck:{deck_id}")
    builder.button(text=deck_msg.BTN_DELETE_DECK, callback_data=f"delete_deck:{deck_id}")
    builder.button(text=common_msg.BTN_BACK_TO_DECKS, callback_data="decks")

    builder.adjust(1)

    return builder.as_markup()


def get_deck_delete_confirm_keyboard(deck_id: int) -> InlineKeyboardMarkup:
    """Get confirmation keyboard for deck deletion.

    Args:
        deck_id: Deck ID

    Returns:
        Inline keyboard with confirmation buttons
    """
    builder = InlineKeyboardBuilder()

    builder.button(text=deck_msg.BTN_CONFIRM_DELETE, callback_data=f"confirm_delete_deck:{deck_id}")
    builder.button(text=common_msg.BTN_CANCEL, callback_data=f"deck:{deck_id}")

    builder.adjust(2)

    return builder.as_markup()
