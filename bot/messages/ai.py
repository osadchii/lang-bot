"""AI assistant messages in Russian."""

MSG_AI_WELCOME = (
    "<b>ИИ-помощник по языку</b>\n\n"
    "Я могу помочь тебе с:\n"
    "- Переводами (греческий - русский)\n"
    "- Объяснениями грамматики\n"
    "- Общими вопросами по языку\n\n"
    "Просто напиши мне свой вопрос!"
)

MSG_TRANSLATE_HELP = "Укажи текст для перевода.\n\nПример: /translate γεια σου"
MSG_GRAMMAR_HELP = "Укажи греческий текст для разбора.\n\nПример: /grammar Το παιδι τρεχει"
MSG_TRANSLATING = "Перевожу..."
MSG_ANALYZING_GRAMMAR = "Анализирую грамматику..."
MSG_THINKING = "Думаю..."


def get_translation_result(translation: str) -> str:
    """Get translation result message.

    Args:
        translation: Translation text

    Returns:
        Formatted translation message
    """
    return f"<b>Перевод:</b>\n\n{translation}"


def get_grammar_result(explanation: str) -> str:
    """Get grammar explanation result message.

    Args:
        explanation: Grammar explanation text

    Returns:
        Formatted explanation message
    """
    return f"<b>Грамматический разбор:</b>\n\n{explanation}"


def get_ai_response(response: str) -> str:
    """Get AI response message.

    Args:
        response: AI response text

    Returns:
        Formatted AI response message
    """
    return f"<b>ИИ-помощник:</b>\n\n{response}"


# AI error messages
MSG_AI_RATE_LIMIT = "Слишком много запросов. Пожалуйста, подожди минуту и попробуй снова."
MSG_AI_TIMEOUT = "Запрос занял слишком много времени. Попробуй более простой запрос."
MSG_AI_CONNECTION_ERROR = (
    "Не удалось подключиться к сервису ИИ. Проверь подключение к интернету и попробуй снова."
)
MSG_AI_SERVICE_ERROR = "Ошибка сервиса ИИ. Попробуй позже."
MSG_AI_UNEXPECTED_ERROR = "Произошла неожиданная ошибка. Попробуй позже."
