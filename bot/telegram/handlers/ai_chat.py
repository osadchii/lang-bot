"""AI assistant handlers."""

from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.user import User
from bot.messages import ai as ai_msg
from bot.messages import common as common_msg
from bot.services.ai_service import AIService
from bot.services.conversation_service import ConversationService
from bot.telegram.keyboards.main_menu import get_main_menu_keyboard

router = Router(name="ai_chat")


@router.message(F.text == common_msg.BTN_AI_ASSISTANT)
async def start_ai_assistant(message: Message):
    """Start AI assistant interaction.

    Args:
        message: Message
    """
    await message.answer(ai_msg.MSG_AI_WELCOME, reply_markup=get_main_menu_keyboard())


@router.message(F.text == "/clear_history")
async def clear_history_command(
    message: Message,
    session: AsyncSession,
    user: User,
    user_created: bool,
):
    """Clear conversation history.

    Args:
        message: Message
        session: Database session
        user: User instance
        user_created: Whether user was just created
    """
    conv_service = ConversationService(session)
    deleted = await conv_service.clear_conversation(user)
    await message.answer(
        ai_msg.get_history_cleared_message(deleted),
        reply_markup=get_main_menu_keyboard(),
    )


@router.message(F.text.startswith("/translate "))
async def translate_command(
    message: Message,
    session: AsyncSession,
    user: User,
    user_created: bool,
):
    """Handle translation command.

    Args:
        message: Message
        session: Database session
        user: User instance
        user_created: Whether user was just created
    """
    text_to_translate = message.text[11:].strip()

    if not text_to_translate:
        await message.answer(ai_msg.MSG_TRANSLATE_HELP)
        return

    thinking_msg = await message.answer(ai_msg.MSG_TRANSLATING)

    conv_service = ConversationService(session)
    await conv_service.add_user_message(
        user=user,
        content=f"/translate {text_to_translate}",
        message_type="translate",
    )

    ai_service = AIService()
    translation = await ai_service.translate_word(text_to_translate)

    await conv_service.add_assistant_message(
        user=user,
        content=translation,
        message_type="translate",
    )

    await thinking_msg.delete()
    await message.answer(ai_msg.get_translation_result(translation))


@router.message(F.text.startswith("/grammar "))
async def grammar_command(
    message: Message,
    session: AsyncSession,
    user: User,
    user_created: bool,
):
    """Handle grammar explanation command.

    Args:
        message: Message
        session: Database session
        user: User instance
        user_created: Whether user was just created
    """
    greek_text = message.text[9:].strip()

    if not greek_text:
        await message.answer(ai_msg.MSG_GRAMMAR_HELP)
        return

    thinking_msg = await message.answer(ai_msg.MSG_ANALYZING_GRAMMAR)

    conv_service = ConversationService(session)
    await conv_service.add_user_message(
        user=user,
        content=f"/grammar {greek_text}",
        message_type="grammar",
    )

    ai_service = AIService()
    explanation = await ai_service.explain_grammar(greek_text)

    await conv_service.add_assistant_message(
        user=user,
        content=explanation,
        message_type="grammar",
    )

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
async def handle_ai_question(
    message: Message,
    session: AsyncSession,
    user: User,
    user_created: bool,
):
    """Handle general AI questions with conversation context.

    Args:
        message: Message
        session: Database session
        user: User instance
        user_created: Whether user was just created
    """
    question = message.text.strip()

    if len(question) < 3:
        return

    thinking_msg = await message.answer(ai_msg.MSG_THINKING)

    conv_service = ConversationService(session)

    history = await conv_service.get_context_messages(user)

    await conv_service.add_user_message(
        user=user,
        content=question,
        message_type="ask_question",
    )

    ai_service = AIService()
    response = await ai_service.ask_question(
        message=question,
        conversation_history=history,
    )

    await conv_service.add_assistant_message(
        user=user,
        content=response,
        message_type="ask_question",
    )

    await thinking_msg.delete()
    await message.answer(ai_msg.get_ai_response(response))
