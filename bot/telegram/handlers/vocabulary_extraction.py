"""Handlers for vocabulary extraction from phrase translations."""

import json

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config.logging_config import get_logger
from bot.database.models.user import User
from bot.messages import vocabulary as vocab_msg
from bot.services.ai_service import AIService
from bot.services.card_service import CardService
from bot.services.deck_service import DeckService
from bot.telegram.keyboards.main_menu import get_main_menu_keyboard
from bot.telegram.keyboards.vocabulary_keyboards import (
    get_deck_selection_for_word_keyboard,
    get_no_decks_keyboard,
    get_word_selection_keyboard,
)
from bot.telegram.states.vocabulary_states import VocabularyExtraction

logger = get_logger(__name__)

router = Router(name="vocabulary_extraction")


def _deserialize_words(data: str | None) -> list[dict] | None:
    """Deserialize words from JSON string.

    Args:
        data: JSON string or None

    Returns:
        List of word dicts or None
    """
    if not data:
        return None
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def _get_card_front_back(word: dict, source_language: str) -> tuple[str, str]:
    """Determine front and back for card based on source language.

    Args:
        word: Word dictionary
        source_language: Source language of the phrase

    Returns:
        Tuple of (front, back)
    """
    if source_language == "greek":
        return word["lemma_with_article"], word["translation"]
    else:
        # Russian phrase - front is Greek translation, back is Russian
        return word["translation"], word["lemma"]


@router.callback_query(F.data.startswith("vocab_show:"))
async def show_extractable_words(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    user_created: bool,
    state: FSMContext,
):
    """Show list of extractable words from the phrase.

    Args:
        callback: Callback query
        session: Database session
        user: User instance
        user_created: Whether user was just created
        state: FSM context
    """
    extraction_hash = callback.data.split(":")[1]
    data = await state.get_data()

    if data.get("extraction_hash") != extraction_hash:
        await callback.answer(vocab_msg.MSG_DATA_EXPIRED)
        await state.clear()
        return

    words_json = data.get("extraction_words")
    words = _deserialize_words(words_json)

    if not words:
        await callback.answer(vocab_msg.MSG_NO_NEW_WORDS)
        await state.clear()
        return

    # Store current word index
    await state.update_data(current_word_index=0)
    await state.set_state(VocabularyExtraction.selecting_words)

    # Show first word
    word = words[0]
    await callback.message.edit_text(
        vocab_msg.get_word_selection_message(
            lemma=word["lemma_with_article"],
            translation=word["translation"],
            original=word["original_form"],
            pos=word["part_of_speech"],
            current_index=1,
            total_count=len(words),
        ),
        reply_markup=get_word_selection_keyboard(
            word_index=0,
            has_next=(len(words) > 1),
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("vocab_add:"), VocabularyExtraction.selecting_words)
async def select_word_for_adding(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    user_created: bool,
    state: FSMContext,
):
    """User selected a word to add - show deck selection with AI suggestion.

    Args:
        callback: Callback query
        session: Database session
        user: User instance
        user_created: Whether user was just created
        state: FSM context
    """
    word_index = int(callback.data.split(":")[1])
    data = await state.get_data()
    words = _deserialize_words(data.get("extraction_words"))
    source_language = data.get("source_language", "greek")

    if not words or word_index >= len(words):
        await callback.answer(vocab_msg.MSG_ERROR)
        await state.clear()
        return

    word = words[word_index]
    front, back = _get_card_front_back(word, source_language)

    # Store selected word index
    await state.update_data(selected_word_index=word_index)
    await state.set_state(VocabularyExtraction.selecting_deck)

    # Get user's decks
    deck_service = DeckService(session)
    decks = await deck_service.get_user_decks(user.id)

    # Get AI suggestion for deck
    suggested_deck_id = None
    suggested_new_name = None

    if decks:
        ai_service = AIService()
        deck_names = [d.name for d in decks]
        suggested_name = await ai_service.suggest_deck_for_word(front, back, deck_names)
        if suggested_name:
            for d in decks:
                if d.name.lower() == suggested_name.lower():
                    suggested_deck_id = d.id
                    break
        if not suggested_deck_id:
            # No matching deck - suggest creating a new one
            suggested_new_name = await ai_service.generate_deck_name(front, back)
    else:
        # No decks - suggest a name for new deck
        ai_service = AIService()
        suggested_new_name = await ai_service.generate_deck_name(front, back)

    if not decks:
        # No decks - show create deck options
        await callback.message.edit_text(
            vocab_msg.MSG_NO_DECKS,
            reply_markup=get_no_decks_keyboard(
                word_index=word_index,
                suggested_name=suggested_new_name,
            ),
        )
    else:
        await callback.message.edit_text(
            vocab_msg.get_deck_selection_for_word(
                lemma=word["lemma_with_article"],
                translation=word["translation"],
            ),
            reply_markup=get_deck_selection_for_word_keyboard(
                decks=decks,
                word_index=word_index,
                suggested_deck_id=suggested_deck_id,
                suggested_new_name=suggested_new_name,
            ),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("vocab_skip:"), VocabularyExtraction.selecting_words)
async def skip_word(
    callback: CallbackQuery,
    state: FSMContext,
):
    """Skip current word and show next.

    Args:
        callback: Callback query
        state: FSM context
    """
    word_index = int(callback.data.split(":")[1])
    data = await state.get_data()
    words = _deserialize_words(data.get("extraction_words"))

    if not words:
        await callback.answer(vocab_msg.MSG_ERROR)
        await state.clear()
        return

    next_index = word_index + 1

    if next_index >= len(words):
        # No more words
        await _finish_extraction(callback, state)
        return

    # Show next word
    word = words[next_index]
    await state.update_data(current_word_index=next_index)

    await callback.message.edit_text(
        vocab_msg.get_word_selection_message(
            lemma=word["lemma_with_article"],
            translation=word["translation"],
            original=word["original_form"],
            pos=word["part_of_speech"],
            current_index=next_index + 1,
            total_count=len(words),
        ),
        reply_markup=get_word_selection_keyboard(
            word_index=next_index,
            has_next=(next_index + 1 < len(words)),
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("vocab_back:"), VocabularyExtraction.selecting_deck)
async def go_back_to_word(
    callback: CallbackQuery,
    state: FSMContext,
):
    """Go back from deck selection to word selection.

    Args:
        callback: Callback query
        state: FSM context
    """
    word_index = int(callback.data.split(":")[1])
    data = await state.get_data()
    words = _deserialize_words(data.get("extraction_words"))

    if not words or word_index >= len(words):
        await callback.answer(vocab_msg.MSG_ERROR)
        await state.clear()
        return

    # Go back to word selection
    await state.set_state(VocabularyExtraction.selecting_words)

    word = words[word_index]
    await callback.message.edit_text(
        vocab_msg.get_word_selection_message(
            lemma=word["lemma_with_article"],
            translation=word["translation"],
            original=word["original_form"],
            pos=word["part_of_speech"],
            current_index=word_index + 1,
            total_count=len(words),
        ),
        reply_markup=get_word_selection_keyboard(
            word_index=word_index,
            has_next=(word_index + 1 < len(words)),
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("vocab_deck:"), VocabularyExtraction.selecting_deck)
async def add_word_to_deck(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    user_created: bool,
    state: FSMContext,
):
    """Add selected word to chosen deck.

    Args:
        callback: Callback query
        session: Database session
        user: User instance
        user_created: Whether user was just created
        state: FSM context
    """
    parts = callback.data.split(":")
    deck_id = int(parts[1])
    word_index = int(parts[2])

    data = await state.get_data()
    words = _deserialize_words(data.get("extraction_words"))
    source_language = data.get("source_language", "greek")

    if not words or word_index >= len(words):
        await callback.answer(vocab_msg.MSG_ERROR)
        await state.clear()
        return

    word = words[word_index]
    front, back = _get_card_front_back(word, source_language)

    # Verify deck
    deck_service = DeckService(session)
    deck = await deck_service.get_deck(deck_id)

    if not deck or deck.user_id != user.id:
        await callback.answer(vocab_msg.MSG_DECK_NOT_FOUND)
        await state.clear()
        return

    # Create card
    try:
        card_service = CardService(session)
        await card_service.create_card(
            deck_id=deck_id,
            front=front,
            back=back,
        )
    except Exception as e:
        logger.exception(f"Failed to create card: {e}")
        await state.clear()
        await callback.answer(vocab_msg.MSG_CARD_CREATE_ERROR)
        return

    # Move to next word
    await _show_next_word_or_finish(callback, state, words, word_index, front, deck.name)


@router.callback_query(F.data.startswith("vocab_new:"), VocabularyExtraction.selecting_deck)
async def create_suggested_deck_and_add(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    user_created: bool,
    state: FSMContext,
):
    """Create deck with suggested name and add card.

    Args:
        callback: Callback query
        session: Database session
        user: User instance
        user_created: Whether user was just created
        state: FSM context
    """
    parts = callback.data.split(":", 2)
    word_index = int(parts[1])
    deck_name = parts[2] if len(parts) > 2 else vocab_msg.DEFAULT_DECK_NAME

    data = await state.get_data()
    words = _deserialize_words(data.get("extraction_words"))
    source_language = data.get("source_language", "greek")

    if not words or word_index >= len(words):
        await callback.answer(vocab_msg.MSG_ERROR)
        await state.clear()
        return

    word = words[word_index]
    front, back = _get_card_front_back(word, source_language)

    try:
        # Create deck
        deck_service = DeckService(session)
        deck = await deck_service.create_deck(user_id=user.id, name=deck_name)

        # Create card
        card_service = CardService(session)
        await card_service.create_card(
            deck_id=deck.id,
            front=front,
            back=back,
        )
    except Exception as e:
        logger.exception(f"Failed to create deck/card: {e}")
        await state.clear()
        await callback.answer(vocab_msg.MSG_CARD_CREATE_ERROR)
        return

    # Move to next word
    await _show_next_word_or_finish(callback, state, words, word_index, front, deck.name)


@router.callback_query(F.data.startswith("vocab_new_custom:"), VocabularyExtraction.selecting_deck)
async def start_custom_deck_creation(
    callback: CallbackQuery,
    state: FSMContext,
):
    """Start custom deck name input.

    Args:
        callback: Callback query
        state: FSM context
    """
    word_index = int(callback.data.split(":")[1])
    await state.update_data(selected_word_index=word_index)
    await state.set_state(VocabularyExtraction.waiting_for_deck_name)
    await callback.message.edit_text(vocab_msg.MSG_ENTER_DECK_NAME)
    await callback.answer()


@router.message(VocabularyExtraction.waiting_for_deck_name)
async def receive_custom_deck_name(
    message: Message,
    session: AsyncSession,
    user: User,
    user_created: bool,
    state: FSMContext,
):
    """Receive custom deck name and create deck with card.

    Args:
        message: Message with deck name
        session: Database session
        user: User instance
        user_created: Whether user was just created
        state: FSM context
    """
    # Validate deck name
    if not message.text:
        await message.answer(vocab_msg.MSG_DECK_NAME_EMPTY)
        return

    deck_name = message.text.strip()

    if not deck_name:
        await message.answer(vocab_msg.MSG_DECK_NAME_EMPTY)
        return

    if len(deck_name) > vocab_msg.MAX_DECK_NAME_LENGTH:
        await message.answer(vocab_msg.MSG_DECK_NAME_TOO_LONG)
        return

    data = await state.get_data()
    words = _deserialize_words(data.get("extraction_words"))
    word_index = data.get("selected_word_index", 0)
    source_language = data.get("source_language", "greek")

    if not words or word_index >= len(words):
        await message.answer(vocab_msg.MSG_ERROR, reply_markup=get_main_menu_keyboard())
        await state.clear()
        return

    word = words[word_index]
    front, back = _get_card_front_back(word, source_language)

    try:
        # Check if deck with this name exists
        deck_service = DeckService(session)
        existing_deck = await deck_service.get_deck_by_name(user.id, deck_name)

        if existing_deck:
            deck = existing_deck
        else:
            deck = await deck_service.create_deck(user_id=user.id, name=deck_name)

        # Create card
        card_service = CardService(session)
        await card_service.create_card(
            deck_id=deck.id,
            front=front,
            back=back,
        )
    except Exception as e:
        logger.exception(f"Failed to create deck/card: {e}")
        await state.clear()
        await message.answer(
            vocab_msg.MSG_CARD_CREATE_ERROR,
            reply_markup=get_main_menu_keyboard(),
        )
        return

    # Move to next word or finish
    next_index = word_index + 1
    if next_index >= len(words):
        # Last word added
        await state.clear()
        await message.answer(
            vocab_msg.get_word_added_final_message(
                front=front,
                back=back,
                deck_name=deck.name,
            ),
            reply_markup=get_main_menu_keyboard(),
        )
        return

    # Show next word
    await state.set_state(VocabularyExtraction.selecting_words)
    next_word = words[next_index]

    await message.answer(
        vocab_msg.get_word_added_continue_message(
            added_front=front,
            deck_name=deck.name,
            next_lemma=next_word["lemma_with_article"],
            next_translation=next_word["translation"],
            next_original=next_word["original_form"],
            current_index=next_index + 1,
            total_count=len(words),
        ),
        reply_markup=get_word_selection_keyboard(
            word_index=next_index,
            has_next=(next_index + 1 < len(words)),
        ),
    )


@router.callback_query(F.data == "vocab_finish")
async def finish_extraction(
    callback: CallbackQuery,
    state: FSMContext,
):
    """Finish vocabulary extraction flow.

    Args:
        callback: Callback query
        state: FSM context
    """
    await _finish_extraction(callback, state)


async def _show_next_word_or_finish(
    callback: CallbackQuery,
    state: FSMContext,
    words: list[dict],
    current_index: int,
    added_front: str,
    deck_name: str,
) -> None:
    """Show next word or finish after adding a card.

    Args:
        callback: Callback query
        state: FSM context
        words: List of words
        current_index: Index of added word
        added_front: Front of added card
        deck_name: Deck name where card was added
    """
    next_index = current_index + 1
    if next_index >= len(words):
        # Last word added
        await callback.message.edit_text(
            vocab_msg.get_word_added_final_message(
                front=added_front,
                back=words[current_index]["translation"],
                deck_name=deck_name,
            ),
            reply_markup=get_main_menu_keyboard(),
        )
        await state.clear()
        await callback.answer()
        return

    # Show next word with confirmation
    await state.set_state(VocabularyExtraction.selecting_words)
    next_word = words[next_index]

    await callback.message.edit_text(
        vocab_msg.get_word_added_continue_message(
            added_front=added_front,
            deck_name=deck_name,
            next_lemma=next_word["lemma_with_article"],
            next_translation=next_word["translation"],
            next_original=next_word["original_form"],
            current_index=next_index + 1,
            total_count=len(words),
        ),
        reply_markup=get_word_selection_keyboard(
            word_index=next_index,
            has_next=(next_index + 1 < len(words)),
        ),
    )
    await callback.answer()


async def _finish_extraction(callback: CallbackQuery, state: FSMContext) -> None:
    """Helper to finish extraction and clear state.

    Args:
        callback: Callback query
        state: FSM context
    """
    await state.clear()
    await callback.message.edit_text(
        vocab_msg.MSG_EXTRACTION_FINISHED,
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()
