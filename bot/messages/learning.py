"""Learning session messages in Russian."""

import html

# Direction indicators for card display
DIRECTION_GREEK_TO_RUSSIAN = "EL -> RU"
DIRECTION_RUSSIAN_TO_GREEK = "RU -> EL"

# Learning start
MSG_NO_DECKS_FOR_LEARNING = (
    "У тебя пока нет колод.\n\nСоздай колоду и добавь карточки, чтобы начать обучение!"
)
MSG_SELECT_DECK_FOR_LEARNING = "<b>Начать обучение</b>\n\nВыбери колоду для изучения:"
MSG_SELECT_DECK_OR_ALL = (
    "<b>Начать обучение</b>\n\n" "Выбери колоду или учи все активные колоды сразу:"
)
MSG_ALL_CARDS_REVIEWED = (
    "<b>Отлично!</b>\n\n"
    "Ты повторил все карточки в этой колоде.\n"
    "Возвращайся позже для дальнейшей практики!"
)
MSG_ALL_DECKS_CARDS_REVIEWED = (
    "<b>Отлично!</b>\n\n"
    "Ты повторил все карточки во всех активных колодах.\n"
    "Возвращайся позже для дальнейшей практики!"
)
MSG_CONTINUE_LEARNING = "<b>Продолжить обучение</b>\n\nВыбери колоду для изучения:"

# Learn all button
BTN_LEARN_ALL = "Учить все колоды"


# Learning session
def get_card_front_message(progress: str, question: str, direction: str) -> str:
    """Get card front display message.

    Args:
        progress: Progress string (e.g., "1/10")
        question: The question text (can be front or back depending on direction)
        direction: Direction hint (e.g., "EL -> RU")

    Returns:
        Card front message
    """
    return (
        f"<b>Сессия обучения</b> ({progress}) <code>{direction}</code>\n\n"
        f"<b>Вопрос:</b>\n{html.escape(question)}\n\n"
        f"Подумай над ответом, затем нажми 'Показать ответ'."
    )


def get_card_answer_message(
    progress: str, question: str, answer: str, example: str | None, direction: str
) -> str:
    """Get card answer display message.

    Args:
        progress: Progress string
        question: The question text
        answer: The answer text
        example: Example sentence (only shown for Greek->Russian direction)
        direction: Direction hint (e.g., "EL -> RU")

    Returns:
        Card answer message
    """
    text = (
        f"<b>Сессия обучения</b> ({progress}) <code>{direction}</code>\n\n"
        f"<b>Вопрос:</b>\n{html.escape(question)}\n\n"
        f"<b>Ответ:</b>\n{html.escape(answer)}\n\n"
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
BTN_FORGOT = "Не помню"
BTN_REMEMBERED = "Вспомнил"
BTN_EASY = "Легко"
BTN_CONTINUE_LEARNING = "Продолжить обучение"
BTN_VIEW_STATISTICS = "Статистика"
BTN_MAIN_MENU = "Главное меню"
