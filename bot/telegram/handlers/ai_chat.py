"""AI assistant handlers."""

from aiogram import F, Router
from aiogram.types import Message

from bot.messages import ai as ai_msg
from bot.messages import common as common_msg
from bot.services.ai_service import AIService
from bot.telegram.keyboards.main_menu import get_main_menu_keyboard

router = Router(name="ai_chat")


@router.message(F.text == common_msg.BTN_AI_ASSISTANT)
async def start_ai_assistant(message: Message):
    """Start AI assistant interaction.

    Args:
        message: Message
    """
    await message.answer(ai_msg.MSG_AI_WELCOME, reply_markup=get_main_menu_keyboard())


@router.message(F.text.startswith("/translate "))
async def translate_command(message: Message):
    """Handle translation command.

    Args:
        message: Message
    """
    text_to_translate = message.text[11:].strip()

    if not text_to_translate:
        await message.answer(ai_msg.MSG_TRANSLATE_HELP)
        return

    thinking_msg = await message.answer(ai_msg.MSG_TRANSLATING)

    ai_service = AIService()
    translation = await ai_service.translate_word(text_to_translate)

    await thinking_msg.delete()
    await message.answer(ai_msg.get_translation_result(translation))


@router.message(F.text.startswith("/grammar "))
async def grammar_command(message: Message):
    """Handle grammar explanation command.

    Args:
        message: Message
    """
    greek_text = message.text[9:].strip()

    if not greek_text:
        await message.answer(ai_msg.MSG_GRAMMAR_HELP)
        return

    thinking_msg = await message.answer(ai_msg.MSG_ANALYZING_GRAMMAR)

    ai_service = AIService()
    explanation = await ai_service.explain_grammar(greek_text)

    await thinking_msg.delete()
    await message.answer(ai_msg.get_grammar_result(explanation))


@router.message(
    F.text
    & ~F.text.startswith("/")
    & ~F.text.in_(
        [
            common_msg.BTN_MY_DECKS,
            common_msg.BTN_LEARN,
            common_msg.BTN_ADD_CARD,
            common_msg.BTN_AI_ASSISTANT,
            common_msg.BTN_STATISTICS,
            common_msg.BTN_HELP,
            common_msg.BTN_CANCEL,
        ]
    )
)
async def handle_ai_question(message: Message):
    """Handle general AI questions.

    Args:
        message: Message
    """
    question = message.text.strip()

    if len(question) < 3:
        return

    thinking_msg = await message.answer(ai_msg.MSG_THINKING)

    ai_service = AIService()
    response = await ai_service.ask_question(question)

    await thinking_msg.delete()
    await message.answer(ai_msg.get_ai_response(response))
