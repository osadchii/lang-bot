"""Deck management messages in Russian."""

import html

# Deck list messages
MSG_NO_DECKS = "<b>У тебя пока нет колод.</b>\n\nСоздай первую колоду, чтобы начать обучение!"


def get_decks_list_message(count: int) -> str:
    """Get deck list header message.

    Args:
        count: Number of decks

    Returns:
        Header message
    """
    return f"<b>Твои колоды ({count})</b>\n\nВыбери колоду для управления:"


# Deck creation messages
MSG_CREATE_DECK_NAME = "<b>Создание новой колоды</b>\n\nВведи название колоды:"
MSG_DECK_NAME_EMPTY = "Название колоды не может быть пустым. Попробуй снова:"
MSG_DECK_NAME_TOO_LONG = "Название колоды слишком длинное (макс. 100 символов). Попробуй снова:"


def get_deck_name_confirm(name: str) -> str:
    """Get deck name confirmation message.

    Args:
        name: Deck name

    Returns:
        Confirmation message
    """
    return (
        f"Название колоды: <b>{html.escape(name)}</b>\n\n"
        f"Теперь введи описание (или отправь /skip, чтобы пропустить):"
    )


def get_deck_created_message(name: str, description: str | None) -> str:
    """Get deck created success message.

    Args:
        name: Deck name
        description: Deck description

    Returns:
        Success message
    """
    desc_text = html.escape(description) if description else "Нет описания"
    return (
        f"<b>Колода успешно создана!</b>\n\n"
        f"<b>Название:</b> {html.escape(name)}\n"
        f"<b>Описание:</b> {desc_text}"
    )


# Deck details messages
def get_deck_details_message(name: str, description: str | None, card_count: int) -> str:
    """Get deck details message.

    Args:
        name: Deck name
        description: Deck description
        card_count: Number of cards

    Returns:
        Details message
    """
    desc_text = html.escape(description) if description else "Нет описания"
    return (
        f"<b>{html.escape(name)}</b>\n\n"
        f"<b>Описание:</b> {desc_text}\n"
        f"<b>Карточек:</b> {card_count}\n\n"
        f"Что хочешь сделать?"
    )


# Deck deletion messages
def get_deck_delete_confirm_message(name: str) -> str:
    """Get deck deletion confirmation message.

    Args:
        name: Deck name

    Returns:
        Confirmation message
    """
    return (
        f"<b>Удалить колоду?</b>\n\n"
        f"Ты уверен, что хочешь удалить <b>{html.escape(name)}</b>?\n"
        f"Все карточки в этой колоде тоже будут удалены!\n\n"
        f"Это действие нельзя отменить."
    )


def get_deck_deleted_message(name: str) -> str:
    """Get deck deleted message.

    Args:
        name: Deck name

    Returns:
        Deleted message
    """
    return f"Колода <b>{html.escape(name)}</b> удалена."


# Deck keyboard button labels
BTN_CREATE_DECK = "Создать новую колоду"
BTN_START_LEARNING = "Начать обучение"
BTN_ADD_CARD_TO_DECK = "Добавить карточку"
BTN_VIEW_CARDS = "Просмотр карточек"
BTN_EDIT_DECK = "Редактировать колоду"
BTN_DELETE_DECK = "Удалить колоду"
BTN_CONFIRM_DELETE = "Да, удалить"
BTN_ENABLE_DECK = "Включить колоду"
BTN_DISABLE_DECK = "Отключить колоду"

# Deck status labels
LABEL_DECK_DISABLED = "(отключена)"

# Deck toggle messages
MSG_DECK_ENABLED = "Колода <b>{name}</b> включена.\nОна будет участвовать в режиме 'Учить все'."
MSG_DECK_DISABLED = (
    "Колода <b>{name}</b> отключена.\nОна не будет участвовать в режиме 'Учить все'."
)


def get_deck_display_name(name: str, is_active: bool) -> str:
    """Get deck display name with status label if disabled.

    Args:
        name: Deck name
        is_active: Whether deck is active

    Returns:
        Display name with optional label
    """
    if is_active:
        return name
    return f"{name} {LABEL_DECK_DISABLED}"


def get_deck_toggle_message(name: str, is_now_active: bool) -> str:
    """Get message for deck toggle action.

    Args:
        name: Deck name
        is_now_active: New active status

    Returns:
        Toggle confirmation message
    """
    if is_now_active:
        return MSG_DECK_ENABLED.format(name=html.escape(name))
    return MSG_DECK_DISABLED.format(name=html.escape(name))
