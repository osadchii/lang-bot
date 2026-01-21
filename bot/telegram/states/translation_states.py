"""FSM states for translation add-to-deck flow."""

from aiogram.fsm.state import State, StatesGroup


class TranslationAddCard(StatesGroup):
    """States for adding a translated word as a card."""

    waiting_for_deck_name = State()  # User provides new deck name
