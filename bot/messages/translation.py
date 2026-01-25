"""Translation feature messages in Russian."""

import html

# Processing messages
MSG_TRANSLATING = "Перевожу..."

# Card exists messages
MSG_CARD_EXISTS_SINGLE = (
    "<b>Перевод:</b>\n\n" "{translation}\n\n" "Это слово уже есть в колоде <b>{deck_name}</b>"
)

MSG_CARD_EXISTS_MULTIPLE = (
    "<b>Перевод:</b>\n\n" "{translation}\n\n" "Это слово уже есть в {count} колодах"
)

# Add to cards messages
MSG_TRANSLATION_WITH_ADD = "<b>Перевод:</b>\n\n{translation}"

MSG_SUGGESTED_DECK = "\n\n<i>Рекомендуемая колода: {deck_name}</i>"

MSG_SELECT_DECK = "<b>Добавить в карточки</b>\n\n" "Выбери колоду для новой карточки:"

MSG_CREATE_FIRST_DECK = "<b>У тебя пока нет колод</b>\n\n" "Введи название для новой колоды:"

MSG_ENTER_DECK_NAME = "Введи название для новой колоды:"

MSG_CARD_ADDED = (
    "<b>Карточка добавлена!</b>\n\n" "<b>{front}</b> - {back}\n\n" "Колода: {deck_name}"
)

MSG_DECK_CREATED_AND_CARD_ADDED = (
    "<b>Колода создана и карточка добавлена!</b>\n\n"
    "Колода: {deck_name}\n"
    "<b>{front}</b> - {back}"
)

# Sentence feedback messages
MSG_SENTENCE_CORRECT = "<b>Правильно!</b>\n\n<b>Перевод:</b>\n{translation}"

MSG_SENTENCE_WITH_ERRORS = (
    "<b>Ошибка:</b> {error_description}\n\n"
    "<b>Исправленный вариант:</b>\n{corrected_sentence}\n\n"
    "<b>Перевод:</b>\n{translation}"
)

MSG_SENTENCE_TRANSLATION_ONLY = "<b>Перевод:</b>\n\n{translation}"

# Error messages
MSG_TRANSLATION_ERROR = "Не удалось получить перевод. Попробуй позже."
MSG_CARD_CREATE_ERROR = "Не удалось создать карточку. Попробуй позже."
MSG_DECK_NAME_TOO_LONG = "Название колоды слишком длинное. Максимум 100 символов."
MSG_DECK_NAME_EMPTY = "Название колоды не может быть пустым."

# Button labels
BTN_ADD_TO_CARDS = "Добавить в карточки"
BTN_CREATE_NEW_DECK = "Создать новую колоду"
BTN_SKIP = "Пропустить"


def get_card_exists_message(translation: str, deck_name: str, count: int = 1) -> str:
    """Get message when card already exists.

    Args:
        translation: Translation text
        deck_name: Name of the deck containing the card
        count: Number of decks containing the card

    Returns:
        Formatted message
    """
    if count == 1:
        return MSG_CARD_EXISTS_SINGLE.format(
            translation=html.escape(translation),
            deck_name=html.escape(deck_name),
        )
    return MSG_CARD_EXISTS_MULTIPLE.format(
        translation=html.escape(translation),
        count=count,
    )


def get_translation_with_add_option(
    translation: str,
    suggested_deck_name: str | None = None,
) -> str:
    """Get translation message with add option.

    Args:
        translation: Translation text
        suggested_deck_name: AI-suggested deck name

    Returns:
        Formatted message
    """
    msg = MSG_TRANSLATION_WITH_ADD.format(translation=html.escape(translation))
    if suggested_deck_name:
        msg += MSG_SUGGESTED_DECK.format(deck_name=html.escape(suggested_deck_name))
    return msg


def get_card_added_message(front: str, back: str, deck_name: str) -> str:
    """Get message for successfully added card.

    Args:
        front: Card front (Greek)
        back: Card back (Russian)
        deck_name: Deck name

    Returns:
        Formatted message
    """
    return MSG_CARD_ADDED.format(
        front=html.escape(front),
        back=html.escape(back),
        deck_name=html.escape(deck_name),
    )


def get_deck_created_message(front: str, back: str, deck_name: str) -> str:
    """Get message for deck created and card added.

    Args:
        front: Card front (Greek)
        back: Card back (Russian)
        deck_name: New deck name

    Returns:
        Formatted message
    """
    return MSG_DECK_CREATED_AND_CARD_ADDED.format(
        front=html.escape(front),
        back=html.escape(back),
        deck_name=html.escape(deck_name),
    )


def get_sentence_feedback_message(
    is_correct: bool,
    translation: str,
    error_description: str | None = None,
    corrected_sentence: str | None = None,
) -> str:
    """Get formatted sentence feedback message.

    Args:
        is_correct: Whether sentence is grammatically correct
        translation: Translation of the sentence
        error_description: Brief description of the error (if any)
        corrected_sentence: Corrected version (if any)

    Returns:
        Formatted feedback message
    """
    if is_correct:
        return MSG_SENTENCE_CORRECT.format(translation=html.escape(translation))

    if error_description and corrected_sentence:
        return MSG_SENTENCE_WITH_ERRORS.format(
            error_description=html.escape(error_description),
            corrected_sentence=html.escape(corrected_sentence),
            translation=html.escape(translation),
        )

    # Fallback if analysis data is missing
    return MSG_SENTENCE_TRANSLATION_ONLY.format(translation=html.escape(translation))
