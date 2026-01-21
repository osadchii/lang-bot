"""Keyboards for translation feature."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models.deck import Deck
from bot.messages import translation as trans_msg


def get_translation_add_keyboard(word_hash: str) -> InlineKeyboardMarkup:
    """Get keyboard for translation result with add option.

    Args:
        word_hash: Short hash to identify the word in callback

    Returns:
        Inline keyboard with add button
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text=trans_msg.BTN_ADD_TO_CARDS,
        callback_data=f"trans_add:{word_hash}",
    )
    builder.adjust(1)
    return builder.as_markup()


def get_deck_selection_keyboard(
    decks: list[Deck],
    suggested_deck_id: int | None = None,
    suggested_new_name: str | None = None,
) -> InlineKeyboardMarkup:
    """Get deck selection keyboard for adding translation.

    Args:
        decks: User's decks
        suggested_deck_id: AI-suggested deck ID (will be marked)
        suggested_new_name: AI-suggested new deck name if no suitable deck

    Returns:
        Inline keyboard
    """
    builder = InlineKeyboardBuilder()

    for deck in decks:
        name = deck.name
        if deck.id == suggested_deck_id:
            name = f"* {name}"
        builder.button(text=name, callback_data=f"trans_deck:{deck.id}")

    # Option to create new deck with AI-suggested name
    if suggested_new_name:
        builder.button(
            text=f"+ {suggested_new_name}",
            callback_data=f"trans_new:{suggested_new_name[:30]}",
        )

    # Always show option to create deck with custom name
    builder.button(
        text=trans_msg.BTN_CREATE_NEW_DECK,
        callback_data="trans_new_custom",
    )

    # Skip option
    builder.button(text=trans_msg.BTN_SKIP, callback_data="trans_skip")

    builder.adjust(1)
    return builder.as_markup()


def get_no_decks_keyboard(suggested_name: str | None = None) -> InlineKeyboardMarkup:
    """Get keyboard when user has no decks.

    Args:
        suggested_name: AI-suggested deck name

    Returns:
        Inline keyboard
    """
    builder = InlineKeyboardBuilder()

    if suggested_name:
        builder.button(
            text=f"+ {suggested_name}",
            callback_data=f"trans_new:{suggested_name[:30]}",
        )

    builder.button(
        text=trans_msg.BTN_CREATE_NEW_DECK,
        callback_data="trans_new_custom",
    )
    builder.button(text=trans_msg.BTN_SKIP, callback_data="trans_skip")

    builder.adjust(1)
    return builder.as_markup()
