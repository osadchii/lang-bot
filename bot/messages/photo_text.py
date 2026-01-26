"""Photo text recognition messages in Russian."""

import html

# Processing messages
MSG_PROCESSING_IMAGE = "Обрабатываю изображение..."

# Error messages
MSG_NO_GREEK_TEXT = (
    "Не удалось найти греческий текст на изображении.\n\n"
    "Попробуй:\n"
    "- Сфотографировать ближе к тексту\n"
    "- Улучшить освещение\n"
    "- Отправить более четкое изображение"
)

MSG_PROCESSING_ERROR = "Не удалось обработать изображение. Попробуй снова позже."

MSG_IMAGE_TOO_LARGE = "Изображение слишком большое. Попробуй отправить файл меньшего размера."

# Result templates
MSG_TEXT_RECOGNIZED = "<b>Распознанный текст:</b>\n<code>{text}</code>"

MSG_TRANSLATION = "\n\n<b>Перевод:</b>\n{translation}"

MSG_PROMPT_RESPONSE = "\n\n<b>Ответ:</b>\n{response}"


def format_photo_result(
    recognized_text: str,
    translation: str,
    prompt_response: str | None = None,
) -> str:
    """Format photo processing result.

    Args:
        recognized_text: Text recognized from image
        translation: Russian translation
        prompt_response: Response to user's prompt (if any)

    Returns:
        Formatted message
    """
    result = MSG_TEXT_RECOGNIZED.format(text=html.escape(recognized_text))
    result += MSG_TRANSLATION.format(translation=html.escape(translation))

    if prompt_response:
        result += MSG_PROMPT_RESPONSE.format(response=html.escape(prompt_response))

    return result


def split_long_message(text: str, max_length: int = 4000) -> list[str]:
    """Split long text into multiple messages.

    Args:
        text: Text to split
        max_length: Maximum characters per message

    Returns:
        List of message chunks
    """
    if len(text) <= max_length:
        return [text]

    chunks = []
    current_chunk = ""

    for paragraph in text.split("\n\n"):
        if len(current_chunk) + len(paragraph) + 2 > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            current_chunk += "\n\n" + paragraph if current_chunk else paragraph

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
