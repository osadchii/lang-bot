"""Unified message handler with AI-powered categorization."""

import json

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config.logging_config import get_logger
from bot.core.message_categories import (
    CONFIDENCE_LOW,
    CategorizationResult,
    LanguageQuestionIntent,
    MessageCategory,
    TextTranslationIntent,
    WordTranslationIntent,
)
from bot.database.models.user import User
from bot.messages import ai as ai_msg
from bot.messages import common as common_msg
from bot.messages import translation as trans_msg
from bot.messages import vocabulary as vocab_msg
from bot.services.ai_service import AIService
from bot.services.conversation_service import ConversationService
from bot.services.message_categorization_service import MessageCategorizationService
from bot.services.translation_service import TranslationService
from bot.services.vocabulary_extraction_service import VocabularyExtractionService
from bot.telegram.keyboards.main_menu import get_main_menu_keyboard
from bot.telegram.keyboards.translation_keyboards import get_translation_add_keyboard
from bot.telegram.keyboards.vocabulary_keyboards import get_vocabulary_extraction_keyboard
from bot.utils.helpers import create_callback_hash

logger = get_logger(__name__)

router = Router(name="unified_message")


@router.message(
    StateFilter(None),
    F.text
    & ~F.text.startswith("/")
    & ~F.text.in_(
        [
            common_msg.BTN_MY_DECKS,
            common_msg.BTN_LEARN,
            common_msg.BTN_ADD_CARD,
            common_msg.BTN_STATISTICS,
            common_msg.BTN_CANCEL,
        ]
    ),
)
async def handle_message(
    message: Message,
    session: AsyncSession,
    user: User,
    user_created: bool,
    state: FSMContext,
):
    """Handle all non-command, non-button text messages.

    Uses AI to categorize the message and routes to appropriate flow.

    Args:
        message: User message
        session: Database session
        user: User instance
        user_created: Whether user was just created
        state: FSM context
    """
    text = message.text.strip()

    if len(text) < 2:
        return  # Ignore very short messages

    # Clear any existing state
    await state.clear()

    # Show thinking indicator
    thinking_msg = await message.answer(ai_msg.MSG_THINKING)

    try:
        # Categorize the message
        categorization_service = MessageCategorizationService()
        result = await categorization_service.categorize_message(text)

        # Log low confidence categorizations
        if not result.is_confident(CONFIDENCE_LOW):
            logger.info(
                f"Low confidence categorization: {result.category.value} ({result.confidence})"
            )

        # Route based on category
        await thinking_msg.delete()

        if result.category == MessageCategory.WORD_TRANSLATION:
            await _handle_word_translation(message, session, user, state, result)
        elif result.category == MessageCategory.TEXT_TRANSLATION:
            await _handle_text_translation(message, session, user, state, result)
        elif result.category == MessageCategory.LANGUAGE_QUESTION:
            await _handle_language_question(message, session, user, result)
        else:
            # Unknown - treat as general question
            await _handle_language_question(message, session, user, result)

    except Exception as e:
        logger.exception(f"Message handling failed: {e}")
        try:
            await thinking_msg.delete()
        except Exception as delete_error:
            logger.debug(f"Failed to delete thinking message: {delete_error}")
        await message.answer(
            common_msg.MSG_ERROR_GENERIC,
            reply_markup=get_main_menu_keyboard(),
        )


async def _handle_word_translation(
    message: Message,
    session: AsyncSession,
    user: User,
    state: FSMContext,
    result: CategorizationResult,
):
    """Handle word translation requests with card check.

    Args:
        message: User message
        session: Database session
        user: User instance
        state: FSM context
        result: Categorization result
    """
    if not isinstance(result.intent, WordTranslationIntent):
        logger.error(f"Expected WordTranslationIntent, got {type(result.intent)}")
        return

    intent = result.intent

    trans_service = TranslationService(session)
    translation_result = await trans_service.translate_with_card_check(
        user=user,
        word=intent.word,
        source_language=intent.source_language,
    )

    if translation_result.existing_card:
        # Card exists - show translation with info
        await message.answer(
            trans_msg.get_card_exists_message(
                translation=translation_result.translation,
                deck_name=(
                    translation_result.existing_deck.name
                    if translation_result.existing_deck
                    else "?"
                ),
                count=translation_result.existing_count,
            ),
            reply_markup=get_main_menu_keyboard(),
        )
    else:
        # Store data for potential add flow
        word_hash = create_callback_hash(translation_result.word)
        suggested_name = (
            translation_result.suggested_deck.name
            if translation_result.suggested_deck
            else translation_result.suggested_deck_name
        )

        await state.update_data(
            word=translation_result.word,
            word_hash=word_hash,
            source_language=translation_result.source_language,
            translation=translation_result.translation,
            suggested_deck_id=(
                translation_result.suggested_deck.id if translation_result.suggested_deck else None
            ),
            suggested_deck_name=translation_result.suggested_deck_name,
        )

        # Show translation with add button
        await message.answer(
            trans_msg.get_translation_with_add_option(
                translation=translation_result.translation,
                suggested_deck_name=suggested_name,
            ),
            reply_markup=get_translation_add_keyboard(word_hash),
        )


async def _handle_text_translation(
    message: Message,
    session: AsyncSession,
    user: User,
    state: FSMContext,
    result: CategorizationResult,
):
    """Handle text/sentence translation requests with feedback and vocabulary extraction.

    Provides feedback on grammatical correctness along with translation.

    Args:
        message: User message
        session: Database session
        user: User instance
        state: FSM context
        result: Categorization result
    """
    if not isinstance(result.intent, TextTranslationIntent):
        logger.error(f"Expected TextTranslationIntent, got {type(result.intent)}")
        return

    intent = result.intent

    # Analyze sentence for errors and get translation with feedback
    trans_service = TranslationService(session)
    analysis = await trans_service.analyze_and_translate_text(
        sentence=intent.text,
        source_language=intent.source_language,
    )

    # Build feedback message
    feedback_message = trans_msg.get_sentence_feedback_message(
        is_correct=analysis.is_correct,
        translation=analysis.translation,
        error_description=analysis.error_description,
        corrected_sentence=analysis.corrected_sentence,
    )

    # Log to conversation history
    conv_service = ConversationService(session)
    await conv_service.add_user_message(
        user=user,
        content=result.raw_message,
        message_type="translate",
    )
    await conv_service.add_assistant_message(
        user=user,
        content=analysis.translation,
        message_type="translate",
    )

    # Extract vocabulary from the phrase
    vocab_service = VocabularyExtractionService(session)
    extraction = await vocab_service.extract_vocabulary(
        user=user,
        phrase=intent.text,
        phrase_translation=analysis.translation,
        source_language=intent.source_language,
    )

    if extraction.new_words:
        # Store extraction data in FSM state
        extraction_hash = create_callback_hash(intent.text)
        words_data = [
            {
                "original_form": w.original_form,
                "lemma": w.lemma,
                "lemma_with_article": w.lemma_with_article,
                "translation": w.translation,
                "part_of_speech": w.part_of_speech,
                "already_in_cards": w.already_in_cards,
            }
            for w in extraction.new_words
        ]
        await state.update_data(
            extraction_hash=extraction_hash,
            extraction_words=json.dumps(words_data, ensure_ascii=False),
            source_language=intent.source_language,
        )

        # Show feedback with "Learn words" button
        await message.answer(
            f"{feedback_message}\n\n{vocab_msg.MSG_VOCABULARY_FOUND.format(count=len(extraction.new_words))}",
            reply_markup=get_vocabulary_extraction_keyboard(extraction_hash),
        )
    elif extraction.existing_words:
        # All words already in cards
        await message.answer(
            f"{feedback_message}\n\n{vocab_msg.MSG_NO_NEW_WORDS}",
            reply_markup=get_main_menu_keyboard(),
        )
    else:
        # No words extracted - show feedback only
        await message.answer(
            feedback_message,
            reply_markup=get_main_menu_keyboard(),
        )


async def _handle_language_question(
    message: Message,
    session: AsyncSession,
    user: User,
    result: CategorizationResult,
):
    """Handle language-related questions.

    Args:
        message: User message
        session: Database session
        user: User instance
        result: Categorization result
    """
    question = (
        result.intent.question
        if isinstance(result.intent, LanguageQuestionIntent)
        else result.raw_message
    )

    conv_service = ConversationService(session)
    history = await conv_service.get_context_messages(user)

    await conv_service.add_user_message(
        user=user,
        content=result.raw_message,
        message_type="ask_question",
    )

    ai_service = AIService()
    response = await ai_service.ask_question(
        message=question,
        conversation_history=history,
    )

    await conv_service.add_assistant_message(
        user=user,
        content=response,
        message_type="ask_question",
    )

    await message.answer(
        ai_msg.get_ai_response(response),
        reply_markup=get_main_menu_keyboard(),
    )
