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

# Card edit messages
MSG_CARD_NOT_FOUND = "Карточка не найдена."


def get_edit_step_1(front: str, back: str, example: str | None) -> str:
    """Get edit step 1 message (editing front).

    Args:
        front: Current front text
        back: Current back text
        example: Current example

    Returns:
        Edit step 1 message
    """
    example_text = html.escape(example) if example else "Нет"
    return (
        f"<b>Редактирование карточки</b>\n\n"
        f"<b>Текущие данные:</b>\n"
        f"- Лицевая сторона: {html.escape(front)}\n"
        f"- Обратная сторона: {html.escape(back)}\n"
        f"- Пример: {example_text}\n\n"
        f"<b>Шаг 1/3:</b> Введи новую <b>лицевую сторону</b>\n"
        f"(или отправь /skip чтобы оставить текущую):"
    )


def get_edit_step_2(front: str) -> str:
    """Get edit step 2 message (editing back).

    Args:
        front: New front text

    Returns:
        Edit step 2 message
    """
    return (
        f"<b>Редактирование карточки</b>\n\n"
        f"Новая лицевая сторона: <b>{html.escape(front)}</b>\n\n"
        f"<b>Шаг 2/3:</b> Введи новую <b>обратную сторону</b>\n"
        f"(или отправь /skip чтобы оставить текущую):"
    )


def get_edit_step_3(front: str, back: str) -> str:
    """Get edit step 3 message (editing example).

    Args:
        front: New front text
        back: New back text

    Returns:
        Edit step 3 message
    """
    return (
        f"<b>Редактирование карточки</b>\n\n"
        f"Лицевая сторона: <b>{html.escape(front)}</b>\n"
        f"Обратная сторона: <b>{html.escape(back)}</b>\n\n"
        f"<b>Шаг 3/3:</b> Введи новый <b>пример использования</b>\n"
        f"(или отправь /skip чтобы оставить текущий, /clear чтобы удалить):"
    )


def get_card_updated_message(front: str, back: str, example: str | None) -> str:
    """Get card updated success message.

    Args:
        front: Updated front text
        back: Updated back text
        example: Updated example

    Returns:
        Success message
    """
    example_text = html.escape(example) if example else "Нет"
    return (
        f"<b>Карточка обновлена!</b>\n\n"
        f"<b>Лицевая сторона:</b> {html.escape(front)}\n"
        f"<b>Обратная сторона:</b> {html.escape(back)}\n"
        f"<b>Пример:</b> {example_text}"
    )


# Card delete messages
def get_delete_confirm_message(front: str, back: str) -> str:
    """Get delete confirmation message.

    Args:
        front: Card front text
        back: Card back text

    Returns:
        Confirmation message
    """
    return (
        f"<b>Удаление карточки</b>\n\n"
        f"Ты уверен, что хочешь удалить карточку?\n\n"
        f"<b>Лицевая сторона:</b> {html.escape(front)}\n"
        f"<b>Обратная сторона:</b> {html.escape(back)}\n\n"
        f"<i>Это действие нельзя отменить.</i>"
    )


MSG_CARD_DELETED = "Карточка успешно удалена."
