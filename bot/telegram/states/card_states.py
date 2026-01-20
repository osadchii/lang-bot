"""FSM states for card management."""

from aiogram.fsm.state import State, StatesGroup


class CardCreation(StatesGroup):
    """States for creating a new card manually."""

    waiting_for_deck = State()
    waiting_for_front = State()
    waiting_for_back = State()
    waiting_for_example = State()


class CardAICreation(StatesGroup):
    """States for creating a card with AI assistance."""

    waiting_for_deck = State()
    waiting_for_word = State()
    waiting_for_confirmation = State()


class CardEdit(StatesGroup):
    """States for editing a card."""

    waiting_for_front = State()
    waiting_for_back = State()
    waiting_for_example = State()
