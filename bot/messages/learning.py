"""Learning session messages in Russian."""

import html

# Learning start
MSG_NO_DECKS_FOR_LEARNING = (
    "У тебя пока нет колод.\n\nСоздай колоду и добавь карточки, чтобы начать обучение!"
)
MSG_SELECT_DECK_FOR_LEARNING = "<b>Начать обучение</b>\n\nВыбери колоду для изучения:"
MSG_ALL_CARDS_REVIEWED = (
    "<b>Отлично!</b>\n\n"
    "Ты повторил все карточки в этой колоде.\n"
    "Возвращайся позже для дальнейшей практики!"
)
MSG_CONTINUE_LEARNING = "<b>Продолжить обучение</b>\n\nВыбери колоду для изучения:"


# Learning session
def get_card_front_message(progress: str, front: str) -> str:
    """Get card front display message.

    Args:
        progress: Progress string (e.g., "1/10")
        front: Card front text

    Returns:
        Card front message
    """
    return (
        f"<b>Сессия обучения</b> ({progress})\n\n"
        f"<b>Вопрос:</b>\n{html.escape(front)}\n\n"
        f"Подумай над ответом, затем нажми 'Показать ответ'."
    )


def get_card_answer_message(progress: str, front: str, back: str, example: str | None) -> str:
    """Get card answer display message.

    Args:
        progress: Progress string
        front: Card front text
        back: Card back text
        example: Example sentence

    Returns:
        Card answer message
    """
    text = (
        f"<b>Сессия обучения</b> ({progress})\n\n"
        f"<b>Вопрос:</b>\n{html.escape(front)}\n\n"
        f"<b>Ответ:</b>\n{html.escape(back)}\n\n"
    )
    if example:
        text += f"<b>Пример:</b>\n{html.escape(example)}\n\n"
    text += "Насколько хорошо ты знал ответ?"
    return text


# Session end
def get_session_complete_message(cards_reviewed: int, correct_count: int, accuracy: float) -> str:
    """Get session complete message.

    Args:
        cards_reviewed: Number of cards reviewed
        correct_count: Number of correct answers
        accuracy: Accuracy percentage

    Returns:
        Session complete message
    """
    return (
        f"<b>Сессия завершена!</b>\n\n"
        f"<b>Карточек повторено:</b> {cards_reviewed}\n"
        f"<b>Правильных ответов:</b> {correct_count}\n"
        f"<b>Точность:</b> {accuracy:.1f}%\n\n"
        f"Отличная работа! Продолжай в том же духе!"
    )


MSG_SESSION_ENDED = "<b>Сессия завершена</b>\n\nКарточки не были повторены."
MSG_MAIN_MENU = "<b>Главное меню</b>\n\nВыбери действие:"

# Learning keyboard button labels
BTN_SHOW_ANSWER = "Показать ответ"
BTN_END_SESSION = "Завершить сессию"
BTN_AGAIN = "Снова"
BTN_HARD = "Трудно"
BTN_GOOD = "Хорошо"
BTN_EASY = "Легко"
BTN_CONTINUE_LEARNING = "Продолжить обучение"
BTN_VIEW_STATISTICS = "Статистика"
BTN_MAIN_MENU = "Главное меню"
