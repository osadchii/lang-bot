"""Exercise session messages in Russian."""

import html

from bot.messages.common import BTN_EXERCISES  # noqa: F401 - re-export for convenience

# Exercise type selection
MSG_SELECT_EXERCISE_TYPE = (
    "<b>Грамматические упражнения</b>\n\n" "Выбери тип упражнения для практики:"
)

BTN_TENSES = "Времена глаголов"
BTN_CONJUGATIONS = "Спряжение глаголов"
BTN_CASES = "Падежи существительных"
BTN_BACK_TO_MENU = "Главное меню"

# Session start
MSG_SESSION_STARTED_TENSES = (
    "<b>Упражнения: Времена</b>\n\n"
    "Тебе будут даны глаголы. Напиши их в указанном времени.\n"
    "Нажми 'Завершить', чтобы закончить сессию."
)
MSG_SESSION_STARTED_CONJUGATIONS = (
    "<b>Упражнения: Спряжение</b>\n\n"
    "Тебе будут даны глаголы. Спрягай их для указанного лица.\n"
    "Нажми 'Завершить', чтобы закончить сессию."
)
MSG_SESSION_STARTED_CASES = (
    "<b>Упражнения: Падежи</b>\n\n"
    "Тебе будут даны существительные. Поставь их в указанный падеж.\n"
    "Нажми 'Завершить', чтобы закончить сессию."
)


def get_task_message(
    word: str,
    translation: str,
    task_text: str,
    task_hint: str,
    total_count: int,
    correct_count: int,
) -> str:
    """Get task display message.

    Args:
        word: Greek word
        translation: Russian translation
        task_text: Task description
        task_hint: Grammar hint
        total_count: Total tasks answered
        correct_count: Correct answers count

    Returns:
        Task message
    """
    accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
    stats = f"Выполнено: {total_count} | Правильно: {correct_count} ({accuracy:.0f}%)"

    return (
        f"<code>{stats}</code>\n\n"
        f"<b>Слово:</b> {html.escape(word)}\n"
        f"<b>Перевод:</b> {html.escape(translation)}\n\n"
        f"<b>Задание:</b> {html.escape(task_text)}\n"
        f"<code>{html.escape(task_hint)}</code>\n\n"
        f"Напиши ответ:"
    )


def get_correct_answer_message(feedback: str) -> str:
    """Get message for correct answer.

    Args:
        feedback: Grammar explanation

    Returns:
        Correct answer message
    """
    return f"<b>Правильно!</b>\n\n{html.escape(feedback)}"


def get_incorrect_answer_message(
    correct_answer: str,
    feedback: str,
) -> str:
    """Get message for incorrect answer.

    Args:
        correct_answer: The correct answer
        feedback: Grammar explanation

    Returns:
        Incorrect answer message
    """
    return (
        f"<b>Неправильно</b>\n\n"
        f"<b>Правильный ответ:</b> {html.escape(correct_answer)}\n\n"
        f"{html.escape(feedback)}"
    )


# Session control buttons
BTN_END_SESSION = "Завершить"
BTN_NEXT_TASK = "Следующее"
BTN_SKIP_TASK = "Пропустить"
BTN_SHOW_ANSWER = "Показать ответ"


def get_shown_answer_message(
    correct_answer: str,
    feedback: str,
) -> str:
    """Get message when user requests to see the answer.

    Args:
        correct_answer: The correct answer
        feedback: Grammar explanation (optional)

    Returns:
        Shown answer message
    """
    text = f"<b>Ответ:</b> {html.escape(correct_answer)}\n\n"
    if feedback:
        text += f"{html.escape(feedback)}"
    return text


def get_session_complete_message(
    total_count: int,
    correct_count: int,
    ai_words_count: int,
) -> str:
    """Get session complete message.

    Args:
        total_count: Total tasks completed
        correct_count: Correct answers
        ai_words_count: Number of AI-generated words

    Returns:
        Session complete message
    """
    accuracy = (correct_count / total_count * 100) if total_count > 0 else 0

    text = (
        f"<b>Сессия завершена!</b>\n\n"
        f"<b>Выполнено упражнений:</b> {total_count}\n"
        f"<b>Правильных ответов:</b> {correct_count}\n"
        f"<b>Точность:</b> {accuracy:.1f}%\n\n"
    )

    if ai_words_count > 0:
        text += f"<b>Новых слов от AI:</b> {ai_words_count}\n\n"

    return text


MSG_SESSION_ENDED_EMPTY = "<b>Сессия завершена</b>\n\nУпражнения не выполнены."

# Add AI words to cards
MSG_OFFER_ADD_AI_WORDS = (
    "Хочешь добавить новые слова в карточки?\n" "Они были сгенерированы во время упражнений."
)
BTN_ADD_AI_WORDS = "Добавить слова в карточки"
BTN_SKIP_ADD_WORDS = "Пропустить"

MSG_WORDS_ADDED = "Слова добавлены в карточки!"
MSG_WORDS_SKIPPED = "Слова не добавлены."

# Exercise type labels (for callbacks)
EXERCISE_TYPE_LABELS = {
    "tenses": "Времена",
    "conjugations": "Спряжение",
    "cases": "Падежи",
}
