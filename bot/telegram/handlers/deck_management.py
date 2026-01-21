"""Deck management handlers."""

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.user import User
from bot.messages import common as common_msg
from bot.messages import decks as deck_msg
from bot.services.deck_service import DeckService
from bot.telegram.keyboards.deck_keyboards import (
    get_deck_actions_keyboard,
    get_deck_delete_confirm_keyboard,
    get_deck_list_keyboard,
)
from bot.telegram.keyboards.main_menu import get_cancel_keyboard, get_main_menu_keyboard
from bot.telegram.states.deck_states import DeckCreation
from bot.telegram.utils.callback_parser import parse_callback_int

router = Router(name="deck_management")


@router.message(F.text == common_msg.BTN_MY_DECKS)
@router.callback_query(F.data == "decks")
async def show_decks(event: Message | CallbackQuery, session: AsyncSession, user: User):
    """Show user's decks.

    Args:
        event: Message or callback query
        session: Database session
        user: User instance
    """
    deck_service = DeckService(session)
    decks = await deck_service.get_user_decks(user.id)

    if not decks:
        text = deck_msg.MSG_NO_DECKS
    else:
        text = deck_msg.get_decks_list_message(len(decks))

    keyboard = get_deck_list_keyboard(decks)

    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard)
    else:
        await event.message.edit_text(text, reply_markup=keyboard)
        await event.answer()


@router.callback_query(F.data == "deck:create")
async def start_deck_creation(callback: CallbackQuery, state: FSMContext):
    """Start deck creation process.

    Args:
        callback: Callback query
        state: FSM state
    """
    await callback.message.edit_text(deck_msg.MSG_CREATE_DECK_NAME)
    await state.set_state(DeckCreation.waiting_for_name)
    await callback.answer()


@router.message(DeckCreation.waiting_for_name)
async def process_deck_name(message: Message, state: FSMContext):
    """Process deck name input.

    Args:
        message: Message with deck name
        state: FSM state
    """
    deck_name = message.text.strip()

    if len(deck_name) < 1:
        await message.answer(deck_msg.MSG_DECK_NAME_EMPTY)
        return

    if len(deck_name) > 100:
        await message.answer(deck_msg.MSG_DECK_NAME_TOO_LONG)
        return

    await state.update_data(deck_name=deck_name)
    await state.set_state(DeckCreation.waiting_for_description)

    await message.answer(
        deck_msg.get_deck_name_confirm(deck_name),
        reply_markup=get_cancel_keyboard(),
    )


@router.message(DeckCreation.waiting_for_description)
async def process_deck_description(
    message: Message, state: FSMContext, session: AsyncSession, user: User
):
    """Process deck description input.

    Args:
        message: Message with description
        state: FSM state
        session: Database session
        user: User instance
    """
    description = None if message.text == "/skip" else message.text.strip()

    # Get deck name from state
    data = await state.get_data()
    deck_name = data.get("deck_name")

    # Create deck
    deck_service = DeckService(session)
    deck = await deck_service.create_deck(user.id, deck_name, description)

    await state.clear()

    await message.answer(
        deck_msg.get_deck_created_message(deck.name, deck.description),
        reply_markup=get_main_menu_keyboard(),
    )


@router.callback_query(F.data.startswith("deck:") & ~F.data.in_(["deck:create"]))
async def show_deck_details(callback: CallbackQuery, session: AsyncSession):
    """Show deck details and actions.

    Args:
        callback: Callback query
        session: Database session
    """
    deck_id = parse_callback_int(callback.data)
    if deck_id is None:
        await callback.answer(common_msg.MSG_INVALID_DATA)
        return

    deck_service = DeckService(session)
    deck, card_count = await deck_service.get_deck_with_stats(deck_id)

    if not deck:
        await callback.answer(common_msg.MSG_INVALID_DATA, show_alert=True)
        return

    text = deck_msg.get_deck_details_message(deck.name, deck.description, card_count)
    await callback.message.edit_text(text, reply_markup=get_deck_actions_keyboard(deck_id))
    await callback.answer()


@router.callback_query(F.data.startswith("delete_deck:"))
async def confirm_deck_deletion(callback: CallbackQuery, session: AsyncSession):
    """Ask for deck deletion confirmation.

    Args:
        callback: Callback query
        session: Database session
    """
    deck_id = parse_callback_int(callback.data)
    if deck_id is None:
        await callback.answer(common_msg.MSG_INVALID_DATA)
        return

    deck_service = DeckService(session)
    deck = await deck_service.get_deck(deck_id)

    if not deck:
        await callback.answer(common_msg.MSG_INVALID_DATA, show_alert=True)
        return

    text = deck_msg.get_deck_delete_confirm_message(deck.name)
    await callback.message.edit_text(text, reply_markup=get_deck_delete_confirm_keyboard(deck_id))
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_deck:"))
async def delete_deck(callback: CallbackQuery, session: AsyncSession, user: User):
    """Delete a deck.

    Args:
        callback: Callback query
        session: Database session
        user: User instance
    """
    deck_id = parse_callback_int(callback.data)
    if deck_id is None:
        await callback.answer(common_msg.MSG_INVALID_DATA)
        return

    deck_service = DeckService(session)
    deck = await deck_service.get_deck(deck_id)

    if not deck:
        await callback.answer(common_msg.MSG_INVALID_DATA, show_alert=True)
        return

    if deck.user_id != user.id:
        await callback.answer(common_msg.MSG_INVALID_DATA, show_alert=True)
        return

    deck_name = deck.name
    await deck_service.delete_deck(deck)

    await callback.message.edit_text(deck_msg.get_deck_deleted_message(deck_name))
    await callback.answer()

    # Show decks list after short delay
    await show_decks(callback, session, user)


@router.message(F.text == common_msg.BTN_CANCEL, StateFilter("*"))
async def cancel_action(message: Message, state: FSMContext):
    """Cancel current action.

    Args:
        message: Message
        state: FSM state
    """
    await state.clear()
    await message.answer(common_msg.MSG_CANCEL_ACTION, reply_markup=get_main_menu_keyboard())
