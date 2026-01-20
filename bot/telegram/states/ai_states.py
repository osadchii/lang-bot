"""FSM states for AI assistant interactions."""

from aiogram.fsm.state import State, StatesGroup


class AIChat(StatesGroup):
    """States for AI chat conversation."""

    in_conversation = State()


class Translation(StatesGroup):
    """States for translation requests."""

    waiting_for_text = State()


class GrammarExplanation(StatesGroup):
    """States for grammar explanation requests."""

    waiting_for_text = State()
