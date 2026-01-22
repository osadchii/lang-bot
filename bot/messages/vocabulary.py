"""Vocabulary extraction feature messages in Russian."""

import html

# Button labels
BTN_LEARN_WORDS = "Изучить слова из фразы"
BTN_ADD_WORD = "Добавить в карточки"
BTN_SKIP_WORD = "Пропустить"
BTN_FINISH = "Закончить"
BTN_BACK = "Назад"
BTN_CREATE_NEW_DECK = "Создать новую колоду"

# Messages
MSG_TRANSLATION_WITH_VOCAB = (
    "<b>Перевод:</b>\n\n" "{translation}\n\n" "Найдено <b>{count}</b> новых слов для изучения"
)

MSG_WORD_SELECTION = (
    "<b>Слово {current}/{total}:</b>\n\n"
    "<b>{lemma}</b>\n"
    "{translation}\n\n"
    "<i>Форма в тексте: {original}</i>\n"
    "<i>Часть речи: {pos}</i>"
)

MSG_DECK_SELECTION_FOR_WORD = (
    "<b>Добавить слово:</b>\n\n" "<b>{lemma}</b> - {translation}\n\n" "Выбери колоду:"
)

MSG_WORD_ADDED = "Карточка <b>{front}</b> - {back} добавлена в колоду <b>{deck}</b>!"

MSG_WORD_ADDED_CONTINUE = (
    "Карточка <b>{front}</b> добавлена в <b>{deck}</b>!\n\n"
    "---\n\n"
    "<b>Слово {current}/{total}:</b>\n\n"
    "<b>{lemma}</b>\n"
    "{translation}\n\n"
    "<i>Форма в тексте: {original}</i>"
)

MSG_EXTRACTION_FINISHED = "Готово!"

MSG_NO_NEW_WORDS = "Все слова из этой фразы уже есть в твоих карточках!"

MSG_DATA_EXPIRED = "Данные устарели. Переведи фразу снова."

MSG_ERROR = "Произошла ошибка. Попробуй снова."

MSG_CARD_CREATE_ERROR = "Не удалось создать карточку. Попробуй позже."

MSG_DECK_NOT_FOUND = "Колода не найдена."

DEFAULT_DECK_NAME = "Разное"

MAX_DECK_NAME_LENGTH = 100

MSG_ENTER_DECK_NAME = "Введи название для новой колоды:"

MSG_DECK_NAME_EMPTY = "Название колоды не может быть пустым."

MSG_DECK_NAME_TOO_LONG = "Название колоды слишком длинное. Максимум 100 символов."

MSG_NO_DECKS = "<b>У тебя пока нет колод</b>\n\nСоздай новую колоду для слова:"

MSG_DECK_CREATED = (
    "<b>Колода создана и карточка добавлена!</b>\n\n"
    "Колода: {deck_name}\n"
    "<b>{front}</b> - {back}"
)

# Part of speech names
POS_NAMES = {
    "noun": "существительное",
    "verb": "глагол",
    "adjective": "прилагательное",
    "adverb": "наречие",
    "pronoun": "местоимение",
    "numeral": "числительное",
    "unknown": "неизвестно",
}


def get_translation_with_vocabulary(translation: str, new_words_count: int) -> str:
    """Get translation message with vocabulary extraction option.

    Args:
        translation: Translation text
        new_words_count: Number of new words found

    Returns:
        Formatted message
    """
    return MSG_TRANSLATION_WITH_VOCAB.format(
        translation=html.escape(translation),
        count=new_words_count,
    )


def get_word_selection_message(
    lemma: str,
    translation: str,
    original: str,
    pos: str,
    current_index: int,
    total_count: int,
) -> str:
    """Get message for word selection.

    Args:
        lemma: Word lemma with article
        translation: Russian translation
        original: Original form in text
        pos: Part of speech
        current_index: Current word index (1-based)
        total_count: Total words count

    Returns:
        Formatted message
    """
    return MSG_WORD_SELECTION.format(
        current=current_index,
        total=total_count,
        lemma=html.escape(lemma),
        translation=html.escape(translation),
        original=html.escape(original),
        pos=POS_NAMES.get(pos, pos),
    )


def get_deck_selection_for_word(lemma: str, translation: str) -> str:
    """Get deck selection message for a word.

    Args:
        lemma: Word lemma with article
        translation: Russian translation

    Returns:
        Formatted message
    """
    return MSG_DECK_SELECTION_FOR_WORD.format(
        lemma=html.escape(lemma),
        translation=html.escape(translation),
    )


def get_word_added_final_message(front: str, back: str, deck_name: str) -> str:
    """Get message when last word is added.

    Args:
        front: Card front (Greek)
        back: Card back (Russian)
        deck_name: Deck name

    Returns:
        Formatted message
    """
    return MSG_WORD_ADDED.format(
        front=html.escape(front),
        back=html.escape(back),
        deck=html.escape(deck_name),
    )


def get_word_added_continue_message(
    added_front: str,
    deck_name: str,
    next_lemma: str,
    next_translation: str,
    next_original: str,
    current_index: int,
    total_count: int,
) -> str:
    """Get message when word is added and there are more.

    Args:
        added_front: Front of the added card
        deck_name: Deck name
        next_lemma: Next word lemma
        next_translation: Next word translation
        next_original: Next word original form
        current_index: Current word index (1-based)
        total_count: Total words count

    Returns:
        Formatted message
    """
    return MSG_WORD_ADDED_CONTINUE.format(
        front=html.escape(added_front),
        deck=html.escape(deck_name),
        current=current_index,
        total=total_count,
        lemma=html.escape(next_lemma),
        translation=html.escape(next_translation),
        original=html.escape(next_original),
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
    return MSG_DECK_CREATED.format(
        front=html.escape(front),
        back=html.escape(back),
        deck_name=html.escape(deck_name),
    )
