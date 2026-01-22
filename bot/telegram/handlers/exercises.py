"""Grammar exercise handlers."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config.logging_config import get_logger
from bot.database.models.user import User
from bot.messages import common as common_msg
from bot.messages import exercises as ex_msg
from bot.services.card_service import CardService
from bot.services.deck_service import DeckService
from bot.services.exercise_service import ExerciseService, ExerciseTask, ExerciseType
from bot.telegram.keyboards.exercise_keyboards import (
    get_after_add_words_keyboard,
    get_exercise_type_keyboard,
    get_feedback_keyboard,
    get_session_end_keyboard,
    get_task_keyboard,
)
from bot.telegram.states.exercise_states import ExerciseSession

logger = get_logger(__name__)

router = Router(name="exercises")


@router.message(F.text == ex_msg.BTN_EXERCISES)
async def show_exercise_types(message: Message, state: FSMContext):
    """Show exercise type selection.

    Args:
        message: Message
        state: FSM state
    """
    await state.clear()
    await message.answer(
        ex_msg.MSG_SELECT_EXERCISE_TYPE,
        reply_markup=get_exercise_type_keyboard(),
    )


@router.callback_query(F.data == "exercises")
async def show_exercise_types_callback(callback: CallbackQuery, state: FSMContext):
    """Show exercise type selection from callback.

    Args:
        callback: Callback query
        state: FSM state
    """
    await state.clear()
    await callback.message.edit_text(
        ex_msg.MSG_SELECT_EXERCISE_TYPE,
        reply_markup=get_exercise_type_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.in_(["exercise:tenses", "exercise:conjugations", "exercise:cases"]))
async def start_exercise_session(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    """Start an exercise session of the selected type.

    Args:
        callback: Callback query
        session: Database session
        state: FSM state
        user: User instance
    """
    exercise_type_str = callback.data.split(":")[1]
    exercise_type = ExerciseType(exercise_type_str)

    # Show session start message
    start_messages = {
        ExerciseType.TENSES: ex_msg.MSG_SESSION_STARTED_TENSES,
        ExerciseType.CONJUGATIONS: ex_msg.MSG_SESSION_STARTED_CONJUGATIONS,
        ExerciseType.CASES: ex_msg.MSG_SESSION_STARTED_CASES,
    }

    # Get user's words with AI supplementation if needed
    exercise_service = ExerciseService(session)
    all_words, session_ai_words = await exercise_service.get_words_with_ai_supplement(
        user_id=user.id,
        exercise_type=exercise_type,
    )

    # Initialize session data
    await state.update_data(
        exercise_type=exercise_type_str,
        total_count=0,
        correct_count=0,
        ai_words=session_ai_words,  # Start with AI-generated supplements
        user_words=all_words,  # Cache all words (user + AI supplements)
        current_task=None,
        exercise_history=[],  # Track recent (word, variation) combinations
    )

    await callback.message.edit_text(start_messages[exercise_type])
    await callback.answer()

    # Generate and show first task
    await generate_and_show_task(callback.message, session, state)


async def generate_and_show_task(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
):
    """Generate a new task and display it.

    Args:
        message: Message to reply to
        session: Database session
        state: FSM state
    """
    data = await state.get_data()
    exercise_type = ExerciseType(data.get("exercise_type"))
    user_words = data.get("user_words", [])
    total_count = data.get("total_count", 0)
    correct_count = data.get("correct_count", 0)
    history = data.get("exercise_history", [])

    exercise_service = ExerciseService(session)

    # Generate task with history tracking
    task, new_history = await exercise_service.generate_task(
        exercise_type=exercise_type,
        user_words=user_words if user_words else None,
        history=history,
    )

    # Store current task and updated history in state
    await state.update_data(
        current_task={
            "word": task.word,
            "translation": task.translation,
            "task_text": task.task_text,
            "task_hint": task.task_hint,
            "expected_answer": task.expected_answer,
            "is_from_ai": task.is_from_ai,
        },
        exercise_history=new_history,
    )

    # Set state to wait for answer
    await state.set_state(ExerciseSession.waiting_for_answer)

    # Show task
    text = ex_msg.get_task_message(
        word=task.word,
        translation=task.translation,
        task_text=task.task_text,
        task_hint=task.task_hint,
        total_count=total_count,
        correct_count=correct_count,
    )

    await message.answer(text, reply_markup=get_task_keyboard())


@router.message(ExerciseSession.waiting_for_answer)
async def process_answer(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    """Process user's answer to the exercise.

    Args:
        message: Message with user's answer
        session: Database session
        state: FSM state
        user: User instance
    """
    user_answer = message.text.strip() if message.text else ""

    if not user_answer:
        await message.answer("Введи ответ или нажми 'Пропустить'.")
        return

    data = await state.get_data()
    current_task = data.get("current_task")
    exercise_type = ExerciseType(data.get("exercise_type"))

    if not current_task:
        await message.answer(common_msg.MSG_ERROR_GENERIC)
        await state.clear()
        return

    # Verify answer
    exercise_service = ExerciseService(session)

    task = ExerciseTask(
        word=current_task["word"],
        translation=current_task["translation"],
        task_text=current_task["task_text"],
        task_hint=current_task["task_hint"],
        expected_answer=current_task["expected_answer"],
        is_from_ai=current_task["is_from_ai"],
    )

    result = await exercise_service.verify_answer(
        task=task,
        user_answer=user_answer,
        exercise_type=exercise_type,
    )

    # Update statistics
    total_count = data.get("total_count", 0) + 1
    correct_count = data.get("correct_count", 0)
    ai_words = data.get("ai_words", [])

    if result.is_correct:
        correct_count += 1

    # If word was from AI, add to list for later
    if current_task["is_from_ai"]:
        ai_words.append(
            {
                "word": current_task["word"],
                "translation": current_task["translation"],
            }
        )

    await state.update_data(
        total_count=total_count,
        correct_count=correct_count,
        ai_words=ai_words,
    )

    # Show feedback
    if result.is_correct:
        text = ex_msg.get_correct_answer_message(result.feedback)
    else:
        text = ex_msg.get_incorrect_answer_message(
            result.correct_answer,
            result.feedback,
        )

    await message.answer(text, reply_markup=get_feedback_keyboard())


@router.callback_query(F.data == "exercise:next")
async def next_task(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
):
    """Generate and show next task.

    Args:
        callback: Callback query
        session: Database session
        state: FSM state
    """
    await callback.message.delete()
    await generate_and_show_task(callback.message, session, state)
    await callback.answer()


@router.callback_query(F.data == "exercise:skip")
async def skip_task(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
):
    """Skip current task and show next.

    Args:
        callback: Callback query
        session: Database session
        state: FSM state
    """
    await callback.message.delete()
    await generate_and_show_task(callback.message, session, state)
    await callback.answer("Пропущено")


@router.callback_query(F.data == "exercise:end")
async def end_session(callback: CallbackQuery, state: FSMContext):
    """End the exercise session.

    Args:
        callback: Callback query
        state: FSM state
    """
    data = await state.get_data()
    total_count = data.get("total_count", 0)
    correct_count = data.get("correct_count", 0)
    ai_words = data.get("ai_words", [])

    if total_count == 0:
        await state.clear()
        await callback.message.edit_text(
            ex_msg.MSG_SESSION_ENDED_EMPTY,
            reply_markup=get_session_end_keyboard(has_ai_words=False),
        )
        await callback.answer()
        return

    text = ex_msg.get_session_complete_message(
        total_count=total_count,
        correct_count=correct_count,
        ai_words_count=len(ai_words),
    )

    has_ai_words = len(ai_words) > 0

    if has_ai_words:
        # Keep data for potential word adding, clear state but not data
        await state.set_state(None)
        text += ex_msg.MSG_OFFER_ADD_AI_WORDS
    else:
        # No AI words to add, clear everything
        await state.clear()

    await callback.message.edit_text(
        text,
        reply_markup=get_session_end_keyboard(has_ai_words=has_ai_words),
    )
    await callback.answer()


@router.callback_query(F.data == "exercise:add_words")
async def add_ai_words_to_cards(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    """Add AI-generated words to user's cards.

    Args:
        callback: Callback query
        session: Database session
        state: FSM state
        user: User instance
    """
    data = await state.get_data()
    ai_words = data.get("ai_words", [])

    if not ai_words:
        await callback.answer("Нет слов для добавления.")
        await state.clear()
        return

    # Get or create a default deck for exercise words
    deck_service = DeckService(session)
    decks = await deck_service.get_user_decks(user.id)

    # Use first deck or create one
    if decks:
        deck = decks[0]
    else:
        deck = await deck_service.create_deck(
            user_id=user.id,
            name="Упражнения",
            description="Слова из упражнений",
        )

    # Add words as cards
    card_service = CardService(session)
    added_count = 0

    for word_data in ai_words:
        try:
            await card_service.create_card(
                deck_id=deck.id,
                front=word_data["word"],
                back=word_data["translation"],
            )
            added_count += 1
        except Exception as e:
            logger.warning(f"Failed to add card for user {user.id}: {word_data['word']} - {e}")

    await state.clear()

    await callback.message.edit_text(
        f"{ex_msg.MSG_WORDS_ADDED}\n\nДобавлено карточек: {added_count}",
        reply_markup=get_after_add_words_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "exercise:skip_words")
async def skip_add_words(callback: CallbackQuery, state: FSMContext):
    """Skip adding AI words to cards.

    Args:
        callback: Callback query
        state: FSM state
    """
    await state.clear()
    await callback.message.edit_text(
        ex_msg.MSG_WORDS_SKIPPED,
        reply_markup=get_after_add_words_keyboard(),
    )
    await callback.answer()
