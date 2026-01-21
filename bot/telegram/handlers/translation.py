"""Smart translation handlers with card integration."""

import hashlib

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config.logging_config import get_logger
from bot.database.models.user import User
from bot.messages import common as common_msg
from bot.messages import translation as trans_msg
from bot.services.card_service import CardService
from bot.services.deck_service import DeckService
from bot.services.translation_service import TranslationService
from bot.telegram.keyboards.main_menu import get_main_menu_keyboard
from bot.telegram.keyboards.translation_keyboards import (
    get_deck_selection_keyboard,
    get_no_decks_keyboard,
    get_translation_add_keyboard,
)
from bot.telegram.states.translation_states import TranslationAddCard
from bot.utils.translation_detector import detect_translation_request

logger = get_logger(__name__)

router = Router(name="translation")


def _hash_word(word: str) -> str:
    """Create a short hash for callback data.

    Args:
        word: Word to hash

    Returns:
        8-character hash
    """
    return hashlib.md5(word.encode()).hexdigest()[:8]


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
async def handle_potential_translation(
    message: Message,
    session: AsyncSession,
    user: User,
    user_created: bool,
    state: FSMContext,
):
    """Handle potential translation requests.

    This handler checks if the message is a translation request.
    If yes, processes it with card check. If no, passes to next handler.

    Args:
        message: Message
        session: Database session
        user: User instance
        user_created: Whether user was just created
        state: FSM context
    """
    request = detect_translation_request(message.text)
    if not request:
        return  # Not a translation request, let other handlers process

    # Clear any existing state
    await state.clear()

    thinking_msg = await message.answer(trans_msg.MSG_TRANSLATING)

    try:
        trans_service = TranslationService(session)
        result = await trans_service.translate_with_card_check(
            user=user,
            word=request.word,
            source_language=request.source_language,
        )
    except Exception as e:
        logger.exception(f"Translation failed: {e}")
        await thinking_msg.delete()
        await message.answer(
            trans_msg.MSG_TRANSLATION_ERROR,
            reply_markup=get_main_menu_keyboard(),
        )
        return

    await thinking_msg.delete()

    if result.existing_card:
        # Card exists - show translation with info
        await message.answer(
            trans_msg.get_card_exists_message(
                translation=result.translation,
                deck_name=result.existing_deck.name if result.existing_deck else "?",
                count=result.existing_count,
            ),
            reply_markup=get_main_menu_keyboard(),
        )
    else:
        # Store data for potential add flow
        word_hash = _hash_word(result.word)
        await state.update_data(
            word=result.word,
            word_hash=word_hash,
            source_language=result.source_language,
            translation=result.translation,
            suggested_deck_id=result.suggested_deck.id if result.suggested_deck else None,
            suggested_deck_name=result.suggested_deck_name,
        )

        # Determine suggested deck name for display
        suggested_name = None
        if result.suggested_deck:
            suggested_name = result.suggested_deck.name
        elif result.suggested_deck_name:
            suggested_name = result.suggested_deck_name

        # Show translation with add button
        await message.answer(
            trans_msg.get_translation_with_add_option(
                translation=result.translation,
                suggested_deck_name=suggested_name,
            ),
            reply_markup=get_translation_add_keyboard(word_hash),
        )


@router.callback_query(F.data.startswith("trans_add:"))
async def start_add_to_deck(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    user_created: bool,
    state: FSMContext,
):
    """Start the add-to-deck flow.

    Args:
        callback: Callback query
        session: Database session
        user: User instance
        user_created: Whether user was just created
        state: FSM context
    """
    # Verify hash matches stored data
    word_hash = callback.data.split(":")[1]
    data = await state.get_data()

    if data.get("word_hash") != word_hash:
        await state.clear()
        await callback.answer("Данные устарели. Попробуй снова.")
        return

    deck_service = DeckService(session)
    decks = await deck_service.get_user_decks(user.id)

    suggested_deck_id = data.get("suggested_deck_id")
    suggested_deck_name = data.get("suggested_deck_name")

    if not decks:
        # No decks - show option to create
        await callback.message.edit_text(
            (
                trans_msg.MSG_CREATE_FIRST_DECK
                if not suggested_deck_name
                else trans_msg.MSG_SELECT_DECK
            ),
            reply_markup=get_no_decks_keyboard(suggested_deck_name),
        )
    else:
        # Show deck selection
        await callback.message.edit_text(
            trans_msg.MSG_SELECT_DECK,
            reply_markup=get_deck_selection_keyboard(
                decks=decks,
                suggested_deck_id=suggested_deck_id,
                suggested_new_name=suggested_deck_name,
            ),
        )

    await callback.answer()


@router.callback_query(F.data.startswith("trans_deck:"))
async def select_existing_deck(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    user_created: bool,
    state: FSMContext,
):
    """Add card to selected existing deck.

    Args:
        callback: Callback query
        session: Database session
        user: User instance
        user_created: Whether user was just created
        state: FSM context
    """
    deck_id = int(callback.data.split(":")[1])
    data = await state.get_data()

    word = data.get("word")
    source_language = data.get("source_language")

    if not word:
        await callback.answer(common_msg.MSG_ERROR_CALLBACK)
        await state.clear()
        return

    # Verify deck belongs to user
    deck_service = DeckService(session)
    deck = await deck_service.get_deck(deck_id)

    if not deck or deck.user_id != user.id:
        await callback.answer(common_msg.MSG_ERROR_CALLBACK)
        return

    await callback.answer("Создаю карточку...")

    try:
        # Generate card data
        trans_service = TranslationService(session)
        card_data = await trans_service.generate_card_data(word, source_language)

        # Create card
        card_service = CardService(session)
        await card_service.create_card(
            deck_id=deck_id,
            front=card_data.front,
            back=card_data.back,
            example=card_data.example if card_data.example else None,
        )
    except Exception as e:
        logger.exception(f"Failed to create card: {e}")
        await state.clear()
        await callback.message.edit_text(trans_msg.MSG_CARD_CREATE_ERROR)
        return

    await state.clear()

    await callback.message.edit_text(
        trans_msg.get_card_added_message(
            front=card_data.front,
            back=card_data.back,
            deck_name=deck.name,
        ),
    )


@router.callback_query(F.data.startswith("trans_new:"))
async def create_suggested_deck(
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
    deck_name = callback.data.split(":", 1)[1]
    data = await state.get_data()

    word = data.get("word")
    source_language = data.get("source_language")

    if not word:
        await callback.answer(common_msg.MSG_ERROR_CALLBACK)
        await state.clear()
        return

    await callback.answer("Создаю колоду и карточку...")

    try:
        # Create deck
        deck_service = DeckService(session)
        deck = await deck_service.create_deck(user_id=user.id, name=deck_name)

        # Generate card data
        trans_service = TranslationService(session)
        card_data = await trans_service.generate_card_data(word, source_language)

        # Create card
        card_service = CardService(session)
        await card_service.create_card(
            deck_id=deck.id,
            front=card_data.front,
            back=card_data.back,
            example=card_data.example if card_data.example else None,
        )
    except Exception as e:
        logger.exception(f"Failed to create deck/card: {e}")
        await state.clear()
        await callback.message.edit_text(trans_msg.MSG_CARD_CREATE_ERROR)
        return

    await state.clear()

    await callback.message.edit_text(
        trans_msg.get_deck_created_message(
            front=card_data.front,
            back=card_data.back,
            deck_name=deck.name,
        ),
    )


@router.callback_query(F.data == "trans_new_custom")
async def start_custom_deck_creation(
    callback: CallbackQuery,
    state: FSMContext,
):
    """Start custom deck name input.

    Args:
        callback: Callback query
        state: FSM context
    """
    await state.set_state(TranslationAddCard.waiting_for_deck_name)
    await callback.message.edit_text(trans_msg.MSG_ENTER_DECK_NAME)
    await callback.answer()


@router.message(TranslationAddCard.waiting_for_deck_name)
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
    deck_name = message.text.strip()

    # Validate deck name
    if not deck_name:
        await message.answer(trans_msg.MSG_DECK_NAME_EMPTY)
        return

    if len(deck_name) > 100:
        await message.answer(trans_msg.MSG_DECK_NAME_TOO_LONG)
        return

    data = await state.get_data()
    word = data.get("word")
    source_language = data.get("source_language")

    if not word:
        await message.answer(common_msg.MSG_ERROR_GENERIC)
        await state.clear()
        return

    try:
        # Check if deck with this name exists
        deck_service = DeckService(session)
        existing_deck = await deck_service.get_deck_by_name(user.id, deck_name)

        if existing_deck:
            deck = existing_deck
        else:
            deck = await deck_service.create_deck(user_id=user.id, name=deck_name)

        # Generate card data
        trans_service = TranslationService(session)
        card_data = await trans_service.generate_card_data(word, source_language)

        # Create card
        card_service = CardService(session)
        await card_service.create_card(
            deck_id=deck.id,
            front=card_data.front,
            back=card_data.back,
            example=card_data.example if card_data.example else None,
        )
    except Exception as e:
        logger.exception(f"Failed to create deck/card: {e}")
        await state.clear()
        await message.answer(
            trans_msg.MSG_CARD_CREATE_ERROR,
            reply_markup=get_main_menu_keyboard(),
        )
        return

    await state.clear()

    if existing_deck:
        await message.answer(
            trans_msg.get_card_added_message(
                front=card_data.front,
                back=card_data.back,
                deck_name=deck.name,
            ),
            reply_markup=get_main_menu_keyboard(),
        )
    else:
        await message.answer(
            trans_msg.get_deck_created_message(
                front=card_data.front,
                back=card_data.back,
                deck_name=deck.name,
            ),
            reply_markup=get_main_menu_keyboard(),
        )


@router.callback_query(F.data == "trans_skip")
async def skip_add_to_deck(
    callback: CallbackQuery,
    state: FSMContext,
):
    """Skip adding to deck.

    Args:
        callback: Callback query
        state: FSM context
    """
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("Пропущено")
