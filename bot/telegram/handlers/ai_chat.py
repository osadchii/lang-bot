"""AI assistant handlers."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.services.ai_service import AIService
from bot.telegram.keyboards.main_menu import get_main_menu_keyboard
from bot.telegram.states.ai_states import AIChat, GrammarExplanation, Translation

router = Router(name="ai_chat")


@router.message(F.text == "🤖 AI Assistant")
async def start_ai_assistant(message: Message):
    """Start AI assistant interaction.

    Args:
        message: Message
    """
    text = (
        "🤖 <b>AI Language Assistant</b>\n\n"
        "I can help you with:\n"
        "• Translations (Greek ↔ English)\n"
        "• Grammar explanations\n"
        "• General language questions\n\n"
        "Just send me a message with your question!"
    )

    await message.answer(text, reply_markup=get_main_menu_keyboard())


@router.message(F.text.startswith("/translate "))
async def translate_command(message: Message):
    """Handle translation command.

    Args:
        message: Message
    """
    text_to_translate = message.text[11:].strip()  # Remove "/translate "

    if not text_to_translate:
        await message.answer(
            "Please provide text to translate.\n\n"
            "Example: /translate γεια σου"
        )
        return

    thinking_msg = await message.answer("🤖 Translating...")

    ai_service = AIService()
    translation = await ai_service.translate_word(text_to_translate)

    await thinking_msg.delete()
    await message.answer(f"<b>Translation:</b>\n\n{translation}")


@router.message(F.text.startswith("/grammar "))
async def grammar_command(message: Message):
    """Handle grammar explanation command.

    Args:
        message: Message
    """
    greek_text = message.text[9:].strip()  # Remove "/grammar "

    if not greek_text:
        await message.answer(
            "Please provide Greek text to explain.\n\n"
            "Example: /grammar Το παιδί τρέχει"
        )
        return

    thinking_msg = await message.answer("🤖 Analyzing grammar...")

    ai_service = AIService()
    explanation = await ai_service.explain_grammar(greek_text)

    await thinking_msg.delete()
    await message.answer(f"<b>Grammar Explanation:</b>\n\n{explanation}")


@router.message(F.text & ~F.text.startswith("/") & ~F.text.in_(
    ["📚 My Decks", "📖 Learn", "➕ Add Card", "🤖 AI Assistant", "📊 Statistics", "❓ Help", "❌ Cancel"]
))
async def handle_ai_question(message: Message):
    """Handle general AI questions.

    Args:
        message: Message
    """
    # Check if message looks like a question or request
    question = message.text.strip()

    if len(question) < 3:
        return  # Ignore very short messages

    thinking_msg = await message.answer("🤖 Thinking...")

    ai_service = AIService()
    response = await ai_service.ask_question(question)

    await thinking_msg.delete()
    await message.answer(f"🤖 <b>AI Assistant:</b>\n\n{response}")
