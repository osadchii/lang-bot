"""Card management handlers."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.user import User
from bot.messages import cards as card_msg
from bot.messages import common as common_msg
from bot.services.ai_service import AIService
from bot.services.card_service import CardService
from bot.services.deck_service import DeckService
from bot.telegram.keyboards.card_keyboards import (
    get_card_actions_keyboard,
    get_card_creation_method_keyboard,
    get_card_list_keyboard,
)
from bot.telegram.keyboards.deck_keyboards import get_deck_list_keyboard
from bot.telegram.keyboards.main_menu import get_cancel_keyboard, get_main_menu_keyboard
from bot.telegram.states.card_states import CardAICreation, CardCreation
from bot.telegram.utils.callback_parser import parse_callback_int
from bot.utils.language_detector import detect_language

router = Router(name="card_management")


@router.message(F.text == common_msg.BTN_ADD_CARD)
async def start_add_card(message: Message, session: AsyncSession, user: User):
    """Start card addition process by selecting deck.

    Args:
        message: Message
        session: Database session
        user: User instance
    """
    deck_service = DeckService(session)
    decks = await deck_service.get_user_decks(user.id)

    if not decks:
        await message.answer(
            card_msg.MSG_NO_DECKS_FOR_CARD,
            reply_markup=get_main_menu_keyboard(),
        )
        return

    keyboard = get_deck_list_keyboard(decks)
    await message.answer(card_msg.MSG_SELECT_DECK_FOR_CARD, reply_markup=keyboard)


@router.callback_query(F.data.startswith("add_card:"))
async def choose_card_creation_method(callback: CallbackQuery):
    """Choose method for creating a card.

    Args:
        callback: Callback query
    """
    deck_id = parse_callback_int(callback.data)
    if deck_id is None:
        await callback.answer(common_msg.MSG_INVALID_DATA)
        return

    await callback.message.edit_text(
        card_msg.MSG_CHOOSE_CREATION_METHOD,
        reply_markup=get_card_creation_method_keyboard(deck_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("create_card_manual:"))
async def start_manual_card_creation(callback: CallbackQuery, state: FSMContext):
    """Start manual card creation.

    Args:
        callback: Callback query
        state: FSM state
    """
    deck_id = parse_callback_int(callback.data)
    if deck_id is None:
        await callback.answer(common_msg.MSG_INVALID_DATA)
        return

    await state.update_data(deck_id=deck_id)
    await state.set_state(CardCreation.waiting_for_front)

    await callback.message.edit_text(card_msg.MSG_CARD_STEP_1)
    await callback.answer()


@router.message(CardCreation.waiting_for_front)
async def process_card_front(message: Message, state: FSMContext):
    """Process front side input.

    Args:
        message: Message
        state: FSM state
    """
    front = message.text.strip()

    await state.update_data(front=front)
    await state.set_state(CardCreation.waiting_for_back)

    await message.answer(
        card_msg.get_card_step_2(front),
        reply_markup=get_cancel_keyboard(),
    )


@router.message(CardCreation.waiting_for_back)
async def process_card_back(message: Message, state: FSMContext):
    """Process back side input.

    Args:
        message: Message
        state: FSM state
    """
    back = message.text.strip()

    await state.update_data(back=back)
    await state.set_state(CardCreation.waiting_for_example)

    data = await state.get_data()
    front = data.get("front")

    await message.answer(
        card_msg.get_card_step_3(front, back),
        reply_markup=get_cancel_keyboard(),
    )


@router.message(CardCreation.waiting_for_example)
async def process_card_example(message: Message, state: FSMContext, session: AsyncSession):
    """Process example sentence and create card.

    Args:
        message: Message
        state: FSM state
        session: Database session
    """
    example = None if message.text == "/skip" else message.text.strip()

    data = await state.get_data()
    deck_id = data.get("deck_id")
    front = data.get("front")
    back = data.get("back")

    # Create card
    card_service = CardService(session)
    card = await card_service.create_card(deck_id=deck_id, front=front, back=back, example=example)

    await state.clear()

    await message.answer(
        card_msg.get_card_created_message(card.front, card.back, card.example),
        reply_markup=get_main_menu_keyboard(),
    )


@router.callback_query(F.data.startswith("create_card_ai:"))
async def start_ai_card_creation(callback: CallbackQuery, state: FSMContext):
    """Start AI-assisted card creation.

    Args:
        callback: Callback query
        state: FSM state
    """
    deck_id = parse_callback_int(callback.data)
    if deck_id is None:
        await callback.answer(common_msg.MSG_INVALID_DATA)
        return

    await state.update_data(deck_id=deck_id)
    await state.set_state(CardAICreation.waiting_for_word)

    await callback.message.edit_text(card_msg.MSG_AI_CARD_PROMPT)
    await callback.answer()


@router.message(CardAICreation.waiting_for_word)
async def process_ai_word(message: Message, state: FSMContext, session: AsyncSession):
    """Process word for AI card generation - supports Greek or Russian input.

    Args:
        message: Message
        state: FSM state
        session: Database session
    """
    word = message.text.strip()

    # Detect language
    source_lang = detect_language(word)

    if source_lang == "unknown":
        await message.answer(
            card_msg.MSG_UNKNOWN_LANGUAGE,
            reply_markup=get_main_menu_keyboard(),
        )
        await state.clear()
        return

    # Show thinking message
    thinking_msg = await message.answer(card_msg.MSG_AI_GENERATING)

    # Generate card with AI using detected language
    ai_service = AIService()
    card_data = await ai_service.generate_card_from_word(word, source_lang)

    await thinking_msg.delete()

    if not card_data.get("back"):
        await message.answer(
            card_msg.MSG_AI_CARD_ERROR,
            reply_markup=get_main_menu_keyboard(),
        )
        await state.clear()
        return

    # Create card
    data = await state.get_data()
    deck_id = data.get("deck_id")

    card_service = CardService(session)
    card = await card_service.create_card(
        deck_id=deck_id,
        front=card_data["front"],
        back=card_data["back"],
        example=card_data.get("example"),
    )

    await state.clear()

    await message.answer(
        card_msg.get_ai_card_created_message(card.front, card.back, card.example),
        reply_markup=get_main_menu_keyboard(),
    )


@router.callback_query(F.data.startswith("view_cards:"))
async def view_deck_cards(callback: CallbackQuery, session: AsyncSession):
    """View cards in a deck.

    Args:
        callback: Callback query
        session: Database session
    """
    parts = callback.data.split(":")
    if len(parts) < 2:
        await callback.answer(common_msg.MSG_INVALID_DATA)
        return

    try:
        deck_id = int(parts[1])
        offset = int(parts[2]) if len(parts) > 2 else 0
    except (ValueError, IndexError):
        await callback.answer(common_msg.MSG_INVALID_DATA)
        return

    card_service = CardService(session)
    cards = await card_service.get_deck_cards(deck_id, limit=10, offset=offset)

    if not cards:
        await callback.message.edit_text(card_msg.MSG_NO_CARDS_IN_DECK)
        await callback.answer()
        return

    text = card_msg.get_cards_list_message(offset, len(cards))
    keyboard = get_card_list_keyboard(cards, deck_id, offset)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("card:"))
async def show_card_details(callback: CallbackQuery, session: AsyncSession):
    """Show card details.

    Args:
        callback: Callback query
        session: Database session
    """
    card_id = parse_callback_int(callback.data)
    if card_id is None:
        await callback.answer(common_msg.MSG_INVALID_DATA)
        return

    card_service = CardService(session)
    card = await card_service.get_card(card_id)

    if not card:
        await callback.answer(common_msg.MSG_INVALID_DATA, show_alert=True)
        return

    text = card_msg.get_card_details_message(
        card.front,
        card.back,
        card.example,
        card.total_reviews,
        card.success_rate,
        card.next_review.strftime("%Y-%m-%d %H:%M"),
    )

    await callback.message.edit_text(
        text, reply_markup=get_card_actions_keyboard(card_id, card.deck_id)
    )
    await callback.answer()
