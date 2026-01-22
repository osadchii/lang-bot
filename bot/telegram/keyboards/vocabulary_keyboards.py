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


def _truncate_for_callback(name: str, prefix: str, max_bytes: int = 64) -> str:
    """Truncate name to fit within callback data byte limit.

    Args:
        name: Name to truncate
        prefix: Callback data prefix
        max_bytes: Maximum total bytes (Telegram limit is 64)

    Returns:
        Truncated name that fits within limit
    """
    prefix_bytes = len(prefix.encode("utf-8"))
    max_name_bytes = max_bytes - prefix_bytes

    # Encode and truncate
    encoded = name.encode("utf-8")
    if len(encoded) <= max_name_bytes:
        return name

    # Truncate bytes and decode safely
    return encoded[:max_name_bytes].decode("utf-8", errors="ignore")


def get_deck_selection_for_word_keyboard(
    decks: list[Deck],
    word_index: int,
    suggested_deck_id: int | None = None,
    suggested_new_name: str | None = None,
) -> InlineKeyboardMarkup:
    """Get deck selection keyboard for adding a word.

    Args:
        decks: User's decks
        word_index: Current word index
        suggested_deck_id: AI-suggested deck ID (will be marked with *)
        suggested_new_name: AI-suggested new deck name if no suitable deck

    Returns:
        Inline keyboard
    """
    builder = InlineKeyboardBuilder()

    for deck in decks:
        name = deck.name
        if deck.id == suggested_deck_id:
            name = f"* {name}"
        builder.button(
            text=name,
            callback_data=f"vocab_deck:{deck.id}:{word_index}",
        )

    # Option to create new deck with AI-suggested name
    if suggested_new_name:
        prefix = f"vocab_new:{word_index}:"
        truncated_name = _truncate_for_callback(suggested_new_name, prefix)
        builder.button(
            text=f"+ {suggested_new_name}",
            callback_data=f"{prefix}{truncated_name}",
        )

    # Always show option to create deck with custom name
    builder.button(
        text=vocab_msg.BTN_CREATE_NEW_DECK,
        callback_data=f"vocab_new_custom:{word_index}",
    )

    # Back button
    builder.button(
        text=vocab_msg.BTN_BACK,
        callback_data=f"vocab_back:{word_index}",
    )

    builder.adjust(1)
    return builder.as_markup()


def get_no_decks_keyboard(
    word_index: int,
    suggested_name: str | None = None,
) -> InlineKeyboardMarkup:
    """Get keyboard when user has no decks.

    Args:
        word_index: Current word index
        suggested_name: AI-suggested deck name

    Returns:
        Inline keyboard
    """
    builder = InlineKeyboardBuilder()

    if suggested_name:
        prefix = f"vocab_new:{word_index}:"
        truncated_name = _truncate_for_callback(suggested_name, prefix)
        builder.button(
            text=f"+ {suggested_name}",
            callback_data=f"{prefix}{truncated_name}",
        )

    builder.button(
        text=vocab_msg.BTN_CREATE_NEW_DECK,
        callback_data=f"vocab_new_custom:{word_index}",
    )

    # Back button
    builder.button(
        text=vocab_msg.BTN_BACK,
        callback_data=f"vocab_back:{word_index}",
    )

    builder.adjust(1)
    return builder.as_markup()
