"""FSM states for vocabulary extraction flow."""

from aiogram.fsm.state import State, StatesGroup


class VocabularyExtraction(StatesGroup):
    """States for vocabulary extraction from phrases."""

    selecting_words = State()  # User browsing extracted words
    selecting_deck = State()  # User selecting deck for a word
    waiting_for_deck_name = State()  # User entering custom deck name
