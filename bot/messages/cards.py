"""Card management messages in Russian."""

import html

# Card list messages
MSG_NO_DECKS_FOR_CARD = "У тебя пока нет колод.\n\nСначала создай колоду через <b>Мои колоды</b>."
MSG_SELECT_DECK_FOR_CARD = "<b>Добавление карточки</b>\n\nВыбери колоду:"
MSG_NO_CARDS_IN_DECK = "В этой колоде пока нет карточек.\n\nДобавь карточки, чтобы начать обучение!"


def get_cards_list_message(offset: int, count: int) -> str:
    """Get cards list header message.

    Args:
        offset: Current offset
        count: Number of cards shown

    Returns:
        Header message
    """
    return f"<b>Карточки в колоде</b> (показаны {offset + 1}-{offset + count}):\n"


# Card creation method selection
MSG_CHOOSE_CREATION_METHOD = "<b>Добавление карточки</b>\n\nКак ты хочешь создать карточку?"
BTN_MANUAL_ENTRY = "Ввести вручную"
BTN_AI_ASSISTANCE = "С помощью ИИ"

# Manual card creation
MSG_CARD_STEP_1 = (
    "<b>Создание карточки - Шаг 1/3</b>\n\n"
    "Введи <b>греческое слово или фразу</b> (лицевая сторона карточки):"
)


def get_card_step_2(front: str) -> str:
    """Get step 2 message.

    Args:
        front: Front side text

    Returns:
        Step 2 message
    """
    return (
        f"Лицевая сторона: <b>{html.escape(front)}</b>\n\n"
        f"<b>Создание карточки - Шаг 2/3</b>\n\n"
        f"Введи <b>русский перевод</b> (обратная сторона карточки):"
    )


def get_card_step_3(front: str, back: str) -> str:
    """Get step 3 message.

    Args:
        front: Front side text
        back: Back side text

    Returns:
        Step 3 message
    """
    return (
        f"Лицевая сторона: <b>{html.escape(front)}</b>\n"
        f"Обратная сторона: <b>{html.escape(back)}</b>\n\n"
        f"<b>Создание карточки - Шаг 3/3</b>\n\n"
        f"Введи <b>пример использования</b> (или отправь /skip):"
    )


def get_card_created_message(front: str, back: str, example: str | None) -> str:
    """Get card created success message.

    Args:
        front: Front side text
        back: Back side text
        example: Example sentence

    Returns:
        Success message
    """
    example_text = html.escape(example) if example else "Нет"
    return (
        f"<b>Карточка успешно создана!</b>\n\n"
        f"<b>Лицевая сторона:</b> {html.escape(front)}\n"
        f"<b>Обратная сторона:</b> {html.escape(back)}\n"
        f"<b>Пример:</b> {example_text}"
    )


# AI card creation
MSG_AI_CARD_PROMPT = (
    "<b>Создание карточки с ИИ</b>\n\n"
    "Введи <b>слово на греческом или русском</b>, и я создам полную карточку для тебя:\n\n"
    "Примеры:\n"
    "- <code>σπίτι</code> (греческое слово)\n"
    "- <code>дом</code> (русское слово)"
)
MSG_AI_GENERATING = "Создаю карточку с помощью ИИ..."
MSG_AI_CARD_ERROR = "Не удалось создать карточку для этого слова. Попробуй другое слово."
MSG_UNKNOWN_LANGUAGE = "Пожалуйста, введи слово на греческом или русском языке."


def get_ai_card_created_message(front: str, back: str, example: str | None) -> str:
    """Get AI card created success message.

    Args:
        front: Front side text
        back: Back side text
        example: Example sentence

    Returns:
        Success message
    """
    example_text = html.escape(example) if example else "Нет"
    return (
        f"<b>Карточка создана с помощью ИИ!</b>\n\n"
        f"<b>Лицевая сторона:</b> {html.escape(front)}\n"
        f"<b>Обратная сторона:</b> {html.escape(back)}\n"
        f"<b>Пример:</b> {example_text}"
    )


# Card details
def get_card_details_message(
    front: str, back: str, example: str | None, reviews: int, success_rate: float, next_review: str
) -> str:
    """Get card details message.

    Args:
        front: Front side text
        back: Back side text
        example: Example sentence
        reviews: Total reviews
        success_rate: Success rate percentage
        next_review: Next review date string

    Returns:
        Details message
    """
    example_text = html.escape(example) if example else "Нет"
    return (
        f"<b>Детали карточки</b>\n\n"
        f"<b>Лицевая сторона:</b> {html.escape(front)}\n"
        f"<b>Обратная сторона:</b> {html.escape(back)}\n"
        f"<b>Пример:</b> {example_text}\n\n"
        f"<b>Статистика:</b>\n"
        f"- Повторений: {reviews}\n"
        f"- Успешность: {success_rate:.1f}%\n"
        f"- Следующее повторение: {next_review}"
    )


# Card keyboard button labels
BTN_EDIT_CARD = "Редактировать"
BTN_DELETE_CARD = "Удалить"
BTN_PREVIOUS = "Назад"
BTN_NEXT = "Вперед"
BTN_BACK_TO_DECK = "К колоде"
BTN_CONFIRM_DELETE = "Да, удалить"
