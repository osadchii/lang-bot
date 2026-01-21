"""Learning session handlers."""

import random
import time

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.user import User
from bot.messages import common as common_msg
from bot.messages import learning as learn_msg
from bot.services.deck_service import DeckService
from bot.services.learning_service import LearningService
from bot.telegram.keyboards.deck_keyboards import get_deck_list_keyboard
from bot.telegram.keyboards.learning_keyboards import (
    get_quality_rating_keyboard,
    get_session_end_keyboard,
    get_show_answer_keyboard,
)
from bot.telegram.keyboards.main_menu import get_main_menu_keyboard
from bot.telegram.utils.callback_parser import parse_callback_int

router = Router(name="learning")


@router.message(F.text == common_msg.BTN_LEARN)
async def start_learning_deck_selection(message: Message, session: AsyncSession, user: User):
    """Start learning by selecting a deck.

    Args:
        message: Message
        session: Database session
        user: User instance
    """
    deck_service = DeckService(session)
    decks = await deck_service.get_user_decks(user.id)

    if not decks:
        await message.answer(
            learn_msg.MSG_NO_DECKS_FOR_LEARNING,
            reply_markup=get_main_menu_keyboard(),
        )
        return

    keyboard = get_deck_list_keyboard(decks)
    await message.answer(learn_msg.MSG_SELECT_DECK_FOR_LEARNING, reply_markup=keyboard)


@router.callback_query(F.data.startswith("learn:"))
async def start_learning_session(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext, user: User
):
    """Start a learning session for a deck.

    Args:
        callback: Callback query
        session: Database session
        state: FSM state
        user: User instance
    """
    deck_id = parse_callback_int(callback.data)
    if deck_id is None:
        await callback.answer(common_msg.MSG_INVALID_DATA)
        return

    learning_service = LearningService(session)

    # Get learning session cards
    session_cards = await learning_service.get_learning_session(deck_id, max_cards=20)

    if not session_cards:
        await callback.message.edit_text(learn_msg.MSG_ALL_CARDS_REVIEWED)
        await callback.answer()
        return

    # Store session data in state
    card_ids = [card.id for card in session_cards]
    await state.update_data(
        deck_id=deck_id,
        card_ids=card_ids,
        current_index=0,
        cards_reviewed=0,
        correct_count=0,
    )

    # Show first card
    await show_card_front(callback, state, session)


async def show_card_front(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Show a random side of the current card as the question.

    Args:
        callback: Callback query
        state: FSM state
        session: Database session
    """
    data = await state.get_data()
    card_ids = data.get("card_ids", [])
    current_index = data.get("current_index", 0)

    if current_index >= len(card_ids):
        await end_learning_session(callback, state)
        return

    card_id = card_ids[current_index]

    from bot.services.card_service import CardService

    card_service = CardService(session)
    card = await card_service.get_card(card_id)

    if not card:
        # Skip this card
        await state.update_data(current_index=current_index + 1)
        await show_card_front(callback, state, session)
        return

    # Randomly choose which side to show as question
    show_front_as_question = random.choice([True, False])

    # Store current card, direction, and timestamp for time tracking
    await state.update_data(
        current_card_id=card_id,
        show_front_as_question=show_front_as_question,
        card_shown_at=time.time(),
    )

    # Determine question text and direction
    if show_front_as_question:
        question_text = card.front
        direction = learn_msg.DIRECTION_GREEK_TO_RUSSIAN
    else:
        question_text = card.back
        direction = learn_msg.DIRECTION_RUSSIAN_TO_GREEK

    progress = f"{current_index + 1}/{len(card_ids)}"
    text = learn_msg.get_card_front_message(progress, question_text, direction)

    await callback.message.edit_text(text, reply_markup=get_show_answer_keyboard())
    await callback.answer()


@router.callback_query(F.data == "show_answer")
async def show_card_answer(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Show the answer side of the card.

    Args:
        callback: Callback query
        state: FSM state
        session: Database session
    """
    data = await state.get_data()
    card_id = data.get("current_card_id")
    card_ids = data.get("card_ids", [])
    current_index = data.get("current_index", 0)
    show_front_as_question = data.get("show_front_as_question", True)

    from bot.services.card_service import CardService

    card_service = CardService(session)
    card = await card_service.get_card(card_id)

    if not card:
        await callback.answer(common_msg.MSG_INVALID_DATA, show_alert=True)
        return

    # Determine question/answer based on stored direction
    if show_front_as_question:
        question_text = card.front
        answer_text = card.back
        direction = learn_msg.DIRECTION_GREEK_TO_RUSSIAN
        example = card.example  # Show example when Greek is question
    else:
        question_text = card.back
        answer_text = card.front
        direction = learn_msg.DIRECTION_RUSSIAN_TO_GREEK
        example = None  # Don't show example when Russian is question

    progress = f"{current_index + 1}/{len(card_ids)}"
    text = learn_msg.get_card_answer_message(
        progress, question_text, answer_text, example, direction
    )

    await callback.message.edit_text(text, reply_markup=get_quality_rating_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("quality:"))
async def process_quality_rating(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, user: User
):
    """Process the quality rating for a card.

    Args:
        callback: Callback query
        state: FSM state
        session: Database session
        user: User instance
    """
    quality = parse_callback_int(callback.data)
    if quality is None:
        await callback.answer(common_msg.MSG_INVALID_DATA)
        return

    data = await state.get_data()
    card_id = data.get("current_card_id")
    current_index = data.get("current_index", 0)
    cards_reviewed = data.get("cards_reviewed", 0)
    correct_count = data.get("correct_count", 0)
    card_shown_at = data.get("card_shown_at")

    # Calculate time spent on this card (capped at 10 minutes)
    time_spent = None
    if card_shown_at is not None:
        time_spent = min(int(time.time() - card_shown_at), 600)

    # Process the review
    learning_service = LearningService(session)
    await learning_service.process_card_review(
        card_id=card_id, user_id=user.id, quality=quality, time_spent=time_spent
    )

    # Update statistics
    cards_reviewed += 1
    if quality >= 3:  # Remembered or Easy
        correct_count += 1

    # Move to next card
    await state.update_data(
        current_index=current_index + 1,
        cards_reviewed=cards_reviewed,
        correct_count=correct_count,
    )

    await show_card_front(callback, state, session)


@router.callback_query(F.data == "end_session")
async def end_learning_session(callback: CallbackQuery, state: FSMContext):
    """End the learning session.

    Args:
        callback: Callback query
        state: FSM state
    """
    data = await state.get_data()
    cards_reviewed = data.get("cards_reviewed", 0)
    correct_count = data.get("correct_count", 0)

    await state.clear()

    if cards_reviewed > 0:
        accuracy = (correct_count / cards_reviewed) * 100
        text = learn_msg.get_session_complete_message(cards_reviewed, correct_count, accuracy)
    else:
        text = learn_msg.MSG_SESSION_ENDED

    await callback.message.edit_text(text, reply_markup=get_session_end_keyboard())
    await callback.answer()


@router.callback_query(F.data == "continue_learning")
async def continue_learning(callback: CallbackQuery, session: AsyncSession, user: User):
    """Continue learning with deck selection.

    Args:
        callback: Callback query
        session: Database session
        user: User instance
    """
    deck_service = DeckService(session)
    decks = await deck_service.get_user_decks(user.id)

    keyboard = get_deck_list_keyboard(decks)
    await callback.message.edit_text(learn_msg.MSG_CONTINUE_LEARNING, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    """Return to main menu.

    Args:
        callback: Callback query
    """
    await callback.message.delete()
    await callback.message.answer(
        learn_msg.MSG_MAIN_MENU,
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()
