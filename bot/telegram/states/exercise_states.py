"""FSM states for grammar exercises."""

from aiogram.fsm.state import State, StatesGroup


class ExerciseSession(StatesGroup):
    """States for exercise session."""

    waiting_for_answer = State()
