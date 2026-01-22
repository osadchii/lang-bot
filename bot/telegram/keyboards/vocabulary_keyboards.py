"""Keyboards for vocabulary extraction feature."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models.deck import Deck
from bot.messages import vocabulary as vocab_msg


def get_vocabulary_extraction_keyboard(extraction_hash: str) -> InlineKeyboardMarkup:
    """Get keyboard for translation with vocabulary extraction option.

    Args:
        extraction_hash: Hash to identify the extraction in callback

    Returns:
        Inline keyboard with learn words button
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text=vocab_msg.BTN_LEARN_WORDS,
        callback_data=f"vocab_show:{extraction_hash}",
    )
    builder.adjust(1)
    return builder.as_markup()


def get_word_selection_keyboard(
    word_index: int,
    has_next: bool,
) -> InlineKeyboardMarkup:
    """Get keyboard for word selection.

    Args:
        word_index: Current word index
        has_next: Whether there are more words

    Returns:
        Inline keyboard
    """
    builder = InlineKeyboardBuilder()

    # Add word button
    builder.button(
        text=vocab_msg.BTN_ADD_WORD,
        callback_data=f"vocab_add:{word_index}",
    )

    # Skip button
    if has_next:
        builder.button(
            text=vocab_msg.BTN_SKIP_WORD,
            callback_data=f"vocab_skip:{word_index}",
        )

    # Finish button
    builder.button(
        text=vocab_msg.BTN_FINISH,
        callback_data="vocab_finish",
    )

    builder.adjust(1)
    return builder.as_markup()


def get_deck_selection_for_word_keyboard(
    decks: list[Deck],
    word_index: int,
) -> InlineKeyboardMarkup:
    """Get deck selection keyboard for adding a word.

    Args:
        decks: User's decks
        word_index: Current word index

    Returns:
        Inline keyboard
    """
    builder = InlineKeyboardBuilder()

    for deck in decks:
        builder.button(
            text=deck.name,
            callback_data=f"vocab_deck:{deck.id}:{word_index}",
        )

    # Back button
    builder.button(
        text=vocab_msg.BTN_BACK,
        callback_data=f"vocab_back:{word_index}",
    )

    builder.adjust(1)
    return builder.as_markup()
