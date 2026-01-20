"""Learning session handlers."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.user import User
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


@router.message(F.text == "📖 Learn")
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
            "❌ You don't have any decks yet.\n\n"
            "Create a deck and add some cards first!",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    text = "📖 <b>Start Learning</b>\n\nSelect a deck to study:"
    keyboard = get_deck_list_keyboard(decks)

    await message.answer(text, reply_markup=keyboard)


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
        await callback.answer("Invalid data")
        return

    learning_service = LearningService(session)

    # Get learning session cards
    session_cards = await learning_service.get_learning_session(deck_id, max_cards=20)

    if not session_cards:
        await callback.message.edit_text(
            "✅ <b>Great job!</b>\n\n"
            "You've reviewed all due cards in this deck.\n"
            "Come back later for more practice!"
        )
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


async def show_card_front(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Show the front of the current card.

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

    # Store current card
    await state.update_data(current_card_id=card_id)

    progress = f"{current_index + 1}/{len(card_ids)}"
    text = (
        f"📖 <b>Learning Session</b> ({progress})\n\n"
        f"<b>Question:</b>\n{card.front}\n\n"
        f"Think of the answer, then click 'Show Answer'."
    )

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

    from bot.services.card_service import CardService

    card_service = CardService(session)
    card = await card_service.get_card(card_id)

    if not card:
        await callback.answer("Card not found", show_alert=True)
        return

    progress = f"{current_index + 1}/{len(card_ids)}"
    text = (
        f"📖 <b>Learning Session</b> ({progress})\n\n"
        f"<b>Question:</b>\n{card.front}\n\n"
        f"<b>Answer:</b>\n{card.back}\n\n"
    )

    if card.example:
        text += f"<b>Example:</b>\n{card.example}\n\n"

    text += "How well did you know it?"

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
        await callback.answer("Invalid data")
        return

    data = await state.get_data()
    card_id = data.get("current_card_id")
    current_index = data.get("current_index", 0)
    cards_reviewed = data.get("cards_reviewed", 0)
    correct_count = data.get("correct_count", 0)

    # Process the review
    learning_service = LearningService(session)
    await learning_service.process_card_review(
        card_id=card_id, user_id=user.id, quality=quality
    )

    # Update statistics
    cards_reviewed += 1
    if quality >= 3:  # Good or Easy
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
        text = (
            f"🎉 <b>Session Complete!</b>\n\n"
            f"<b>Cards Reviewed:</b> {cards_reviewed}\n"
            f"<b>Correct Answers:</b> {correct_count}\n"
            f"<b>Accuracy:</b> {accuracy:.1f}%\n\n"
            f"Great work! Keep it up!"
        )
    else:
        text = "📖 <b>Session Ended</b>\n\nNo cards were reviewed."

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

    text = "📖 <b>Continue Learning</b>\n\nSelect a deck to study:"
    keyboard = get_deck_list_keyboard(decks)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    """Return to main menu.

    Args:
        callback: Callback query
    """
    await callback.message.edit_text(
        "🏠 <b>Main Menu</b>\n\nSelect an option:",
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()
