"""Handlers for vocabulary extraction from phrase translations."""

import json

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config.logging_config import get_logger
from bot.database.models.user import User
from bot.messages import vocabulary as vocab_msg
from bot.services.card_service import CardService
from bot.services.deck_service import DeckService
from bot.telegram.keyboards.main_menu import get_main_menu_keyboard
from bot.telegram.keyboards.vocabulary_keyboards import (
    get_deck_selection_for_word_keyboard,
    get_word_selection_keyboard,
)
from bot.telegram.states.vocabulary_states import VocabularyExtraction

logger = get_logger(__name__)

router = Router(name="vocabulary_extraction")


def _serialize_words(words: list) -> str:
    """Serialize extracted words to JSON string.

    Args:
        words: List of ExtractedWord objects

    Returns:
        JSON string
    """
    data = []
    for w in words:
        data.append(
            {
                "original_form": w.original_form,
                "lemma": w.lemma,
                "lemma_with_article": w.lemma_with_article,
                "translation": w.translation,
                "part_of_speech": w.part_of_speech,
                "already_in_cards": w.already_in_cards,
            }
        )
    return json.dumps(data, ensure_ascii=False)


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
    """User selected a word to add - show deck selection.

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

    if not words or word_index >= len(words):
        await callback.answer(vocab_msg.MSG_ERROR)
        await state.clear()
        return

    word = words[word_index]

    # Store selected word index
    await state.update_data(selected_word_index=word_index)
    await state.set_state(VocabularyExtraction.selecting_deck)

    # Get user's decks
    deck_service = DeckService(session)
    decks = await deck_service.get_user_decks(user.id)

    await callback.message.edit_text(
        vocab_msg.get_deck_selection_for_word(
            lemma=word["lemma_with_article"],
            translation=word["translation"],
        ),
        reply_markup=get_deck_selection_for_word_keyboard(
            decks=decks,
            word_index=word_index,
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
        return

    word = words[word_index]

    # Verify deck
    deck_service = DeckService(session)
    deck = await deck_service.get_deck(deck_id)

    if not deck or deck.user_id != user.id:
        await callback.answer("Колода не найдена.")
        return

    # Create card
    card_service = CardService(session)

    # Determine front/back based on source language
    if source_language == "greek":
        front = word["lemma_with_article"]
        back = word["translation"]
    else:
        # Russian phrase - front is Greek translation, back is Russian
        front = word["translation"]
        back = word["lemma"]

    await card_service.create_card(
        deck_id=deck_id,
        front=front,
        back=back,
    )

    # Move to next word
    next_index = word_index + 1
    if next_index >= len(words):
        # Last word added
        await callback.message.edit_text(
            vocab_msg.get_word_added_final_message(
                front=front,
                back=back,
                deck_name=deck.name,
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
    await callback.answer()


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
