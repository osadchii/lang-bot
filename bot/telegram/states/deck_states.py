"""FSM states for deck management."""

from aiogram.fsm.state import State, StatesGroup


class DeckCreation(StatesGroup):
    """States for creating a new deck."""

    waiting_for_name = State()
    waiting_for_description = State()


class DeckEdit(StatesGroup):
    """States for editing a deck."""

    waiting_for_new_name = State()
    waiting_for_new_description = State()
