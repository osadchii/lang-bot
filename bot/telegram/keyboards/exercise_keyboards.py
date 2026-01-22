"""Keyboards for grammar exercises."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.messages import exercises as ex_msg


def get_exercise_type_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard with exercise type selection.

    Returns:
        Inline keyboard with exercise types
    """
    builder = InlineKeyboardBuilder()

    builder.button(text=ex_msg.BTN_TENSES, callback_data="exercise:tenses")
    builder.button(text=ex_msg.BTN_CONJUGATIONS, callback_data="exercise:conjugations")
    builder.button(text=ex_msg.BTN_CASES, callback_data="exercise:cases")
    builder.button(text=ex_msg.BTN_BACK_TO_MENU, callback_data="main_menu")

    builder.adjust(1)

    return builder.as_markup()


def get_task_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard shown during task (while waiting for answer).

    Returns:
        Inline keyboard with show answer/skip/end options
    """
    builder = InlineKeyboardBuilder()

    builder.button(text=ex_msg.BTN_SHOW_ANSWER, callback_data="exercise:show_answer")
    builder.button(text=ex_msg.BTN_SKIP_TASK, callback_data="exercise:skip")
    builder.button(text=ex_msg.BTN_END_SESSION, callback_data="exercise:end")

    builder.adjust(2, 1)  # First row: Show Answer + Skip, Second row: Finish

    return builder.as_markup()


def get_feedback_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard shown after answer feedback.

    Returns:
        Inline keyboard with next/end options
    """
    builder = InlineKeyboardBuilder()

    builder.button(text=ex_msg.BTN_NEXT_TASK, callback_data="exercise:next")
    builder.button(text=ex_msg.BTN_END_SESSION, callback_data="exercise:end")

    builder.adjust(2)

    return builder.as_markup()


def get_session_end_keyboard(has_ai_words: bool = False) -> InlineKeyboardMarkup:
    """Get keyboard shown at session end.

    Args:
        has_ai_words: Whether there are AI words to add

    Returns:
        Inline keyboard with session end options
    """
    builder = InlineKeyboardBuilder()

    if has_ai_words:
        builder.button(text=ex_msg.BTN_ADD_AI_WORDS, callback_data="exercise:add_words")
        builder.button(text=ex_msg.BTN_SKIP_ADD_WORDS, callback_data="exercise:skip_words")
        builder.adjust(1)
    else:
        builder.button(text=ex_msg.BTN_EXERCISES, callback_data="exercises")
        builder.button(text=ex_msg.BTN_BACK_TO_MENU, callback_data="main_menu")
        builder.adjust(1)

    return builder.as_markup()


def get_after_add_words_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard shown after adding words.

    Returns:
        Inline keyboard with navigation options
    """
    builder = InlineKeyboardBuilder()

    builder.button(text=ex_msg.BTN_EXERCISES, callback_data="exercises")
    builder.button(text=ex_msg.BTN_BACK_TO_MENU, callback_data="main_menu")

    builder.adjust(1)

    return builder.as_markup()
