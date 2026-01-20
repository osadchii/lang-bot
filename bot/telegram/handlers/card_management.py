"""Card management handlers."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.user import User
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
from bot.telegram.utils.callback_parser import parse_callback_data, parse_callback_int

router = Router(name="card_management")


@router.message(F.text == "➕ Add Card")
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
            "❌ You don't have any decks yet.\n\n"
            "Create a deck first using <b>📚 My Decks</b>.",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    text = "📝 <b>Add New Card</b>\n\nSelect a deck:"
    keyboard = get_deck_list_keyboard(decks)

    # Modify keyboard to use add_card callbacks
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("add_card:"))
async def choose_card_creation_method(callback: CallbackQuery):
    """Choose method for creating a card.

    Args:
        callback: Callback query
    """
    deck_id = parse_callback_int(callback.data)
    if deck_id is None:
        await callback.answer("Invalid data")
        return

    text = (
        "📝 <b>Add New Card</b>\n\n"
        "How would you like to create the card?"
    )

    await callback.message.edit_text(
        text, reply_markup=get_card_creation_method_keyboard(deck_id)
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
        await callback.answer("Invalid data")
        return

    await state.update_data(deck_id=deck_id)
    await state.set_state(CardCreation.waiting_for_front)

    await callback.message.edit_text(
        "📝 <b>Create Card - Step 1/3</b>\n\n"
        "Enter the <b>Greek word or phrase</b> (front of card):"
    )
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
        f"✅ Front: <b>{front}</b>\n\n"
        f"📝 <b>Create Card - Step 2/3</b>\n\n"
        f"Enter the <b>English translation</b> (back of card):",
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
        f"✅ Front: <b>{front}</b>\n"
        f"✅ Back: <b>{back}</b>\n\n"
        f"📝 <b>Create Card - Step 3/3</b>\n\n"
        f"Enter an <b>example sentence</b> (or send /skip):",
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
    card = await card_service.create_card(
        deck_id=deck_id, front=front, back=back, example=example
    )

    await state.clear()

    await message.answer(
        f"✅ <b>Card created successfully!</b>\n\n"
        f"<b>Front:</b> {card.front}\n"
        f"<b>Back:</b> {card.back}\n"
        f"<b>Example:</b> {card.example or 'None'}",
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
        await callback.answer("Invalid data")
        return

    await state.update_data(deck_id=deck_id)
    await state.set_state(CardAICreation.waiting_for_word)

    await callback.message.edit_text(
        "🤖 <b>AI Card Creation</b>\n\n"
        "Enter a <b>Greek word</b> and I'll create a complete flashcard for you:"
    )
    await callback.answer()


@router.message(CardAICreation.waiting_for_word)
async def process_ai_word(message: Message, state: FSMContext, session: AsyncSession):
    """Process word for AI card generation.

    Args:
        message: Message
        state: FSM state
        session: Database session
    """
    word = message.text.strip()

    # Show thinking message
    thinking_msg = await message.answer("🤖 Generating card with AI...")

    # Generate card with AI
    ai_service = AIService()
    card_data = await ai_service.generate_card_from_word(word)

    await thinking_msg.delete()

    if not card_data.get("back"):
        await message.answer(
            "❌ Sorry, I couldn't generate a card for that word. Please try again.",
            reply_markup=get_main_menu_keyboard(),
        )
        await state.clear()
        return

    # Save to state
    await state.update_data(**card_data)

    # Show preview and create
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
        f"✅ <b>AI Card Created!</b>\n\n"
        f"<b>Front:</b> {card.front}\n"
        f"<b>Back:</b> {card.back}\n"
        f"<b>Example:</b> {card.example or 'None'}",
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
        await callback.answer("Invalid data")
        return

    try:
        deck_id = int(parts[1])
        offset = int(parts[2]) if len(parts) > 2 else 0
    except (ValueError, IndexError):
        await callback.answer("Invalid data")
        return

    card_service = CardService(session)
    cards = await card_service.get_deck_cards(deck_id, limit=10, offset=offset)

    if not cards:
        await callback.message.edit_text(
            "📝 This deck has no cards yet.\n\n"
            "Add some cards to start learning!"
        )
        await callback.answer()
        return

    text = f"📝 <b>Cards in Deck</b> (showing {offset + 1}-{offset + len(cards)}):\n\n"

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
        await callback.answer("Invalid data")
        return

    card_service = CardService(session)
    card = await card_service.get_card(card_id)

    if not card:
        await callback.answer("❌ Card not found", show_alert=True)
        return

    text = (
        f"📝 <b>Card Details</b>\n\n"
        f"<b>Front:</b> {card.front}\n"
        f"<b>Back:</b> {card.back}\n"
        f"<b>Example:</b> {card.example or 'None'}\n\n"
        f"<b>Stats:</b>\n"
        f"• Reviews: {card.total_reviews}\n"
        f"• Success Rate: {card.success_rate:.1f}%\n"
        f"• Next Review: {card.next_review.strftime('%Y-%m-%d %H:%M')}"
    )

    await callback.message.edit_text(
        text, reply_markup=get_card_actions_keyboard(card_id, card.deck_id)
    )
    await callback.answer()
