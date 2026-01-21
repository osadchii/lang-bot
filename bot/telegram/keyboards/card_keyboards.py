"""Keyboards for card management."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models.card import Card
from bot.messages import cards as card_msg
from bot.messages import common as common_msg


def get_card_creation_method_keyboard(deck_id: int) -> InlineKeyboardMarkup:
    """Get keyboard to choose card creation method.

    Args:
        deck_id: Deck ID

    Returns:
        Inline keyboard with creation method buttons
    """
    builder = InlineKeyboardBuilder()

    builder.button(text=card_msg.BTN_MANUAL_ENTRY, callback_data=f"create_card_manual:{deck_id}")
    builder.button(text=card_msg.BTN_AI_ASSISTANCE, callback_data=f"create_card_ai:{deck_id}")
    builder.button(text=common_msg.BTN_CANCEL, callback_data=f"deck:{deck_id}")

    builder.adjust(1)

    return builder.as_markup()


def get_card_actions_keyboard(card_id: int, deck_id: int) -> InlineKeyboardMarkup:
    """Get keyboard with card actions.

    Args:
        card_id: Card ID
        deck_id: Deck ID

    Returns:
        Inline keyboard with card action buttons
    """
    builder = InlineKeyboardBuilder()

    builder.button(text=card_msg.BTN_EDIT_CARD, callback_data=f"edit_card:{card_id}")
    builder.button(text=card_msg.BTN_DELETE_CARD, callback_data=f"delete_card:{card_id}")
    builder.button(text=common_msg.BTN_BACK, callback_data=f"view_cards:{deck_id}")

    builder.adjust(2, 1)

    return builder.as_markup()


def get_card_list_keyboard(
    cards: list[Card], deck_id: int, offset: int = 0
) -> InlineKeyboardMarkup:
    """Get keyboard with list of cards.

    Args:
        cards: List of card instances
        deck_id: Deck ID
        offset: Current offset for pagination

    Returns:
        Inline keyboard with card buttons
    """
    builder = InlineKeyboardBuilder()

    for card in cards:
        front_preview = card.front[:30] + "..." if len(card.front) > 30 else card.front
        builder.button(text=front_preview, callback_data=f"card:{card.id}")

    # Pagination buttons
    nav_buttons = []
    if offset > 0:
        nav_buttons.append((card_msg.BTN_PREVIOUS, f"view_cards:{deck_id}:{offset - 10}"))
    if len(cards) == 10:
        nav_buttons.append((card_msg.BTN_NEXT, f"view_cards:{deck_id}:{offset + 10}"))

    for text, callback in nav_buttons:
        builder.button(text=text, callback_data=callback)

    builder.button(text=card_msg.BTN_BACK_TO_DECK, callback_data=f"deck:{deck_id}")

    builder.adjust(1)

    return builder.as_markup()


def get_card_delete_confirm_keyboard(card_id: int, deck_id: int) -> InlineKeyboardMarkup:
    """Get confirmation keyboard for card deletion.

    Args:
        card_id: Card ID
        deck_id: Deck ID

    Returns:
        Inline keyboard with confirmation buttons
    """
    builder = InlineKeyboardBuilder()

    builder.button(text=card_msg.BTN_CONFIRM_DELETE, callback_data=f"confirm_delete_card:{card_id}")
    builder.button(text=common_msg.BTN_CANCEL, callback_data=f"card:{card_id}")

    builder.adjust(2)

    return builder.as_markup()
