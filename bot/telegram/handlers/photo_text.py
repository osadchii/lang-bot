"""Handler for photo messages with Greek text recognition."""

import base64
import json

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config.logging_config import get_logger
from bot.config.settings import settings
from bot.database.models.user import User
from bot.messages import photo_text as photo_msg
from bot.messages import vocabulary as vocab_msg
from bot.services.ai_service import AIService
from bot.services.vocabulary_extraction_service import VocabularyExtractionService
from bot.telegram.keyboards.main_menu import get_main_menu_keyboard
from bot.telegram.keyboards.vocabulary_keyboards import get_vocabulary_extraction_keyboard
from bot.utils.helpers import create_callback_hash

logger = get_logger(__name__)

router = Router(name="photo_text")


@router.message(F.photo)
async def handle_photo(
    message: Message,
    session: AsyncSession,
    user: User,
    user_created: bool,
    state: FSMContext,
):
    """Handle photo messages for Greek text recognition.

    Uses OpenAI Vision API to recognize Greek text from photos
    and process it according to user's caption (if provided).
    Also extracts vocabulary for card creation.

    Args:
        message: Message with photo
        session: Database session
        user: User instance
        user_created: Whether user was just created
        state: FSM context for vocabulary extraction
    """
    # Get user's caption (prompt) if any
    user_prompt = message.caption.strip() if message.caption else None

    # Show processing indicator
    processing_msg = await message.answer(photo_msg.MSG_PROCESSING_IMAGE)

    try:
        # Get largest photo size (best quality)
        photo = message.photo[-1]

        # Get file info and check size
        file = await message.bot.get_file(photo.file_id)
        max_size_bytes = int(settings.max_image_size_mb * 1024 * 1024)

        if file.file_size and file.file_size > max_size_bytes:
            try:
                await processing_msg.delete()
            except Exception as e:
                logger.debug(f"Failed to delete processing message: {e}")
            await message.answer(
                photo_msg.MSG_IMAGE_TOO_LARGE,
                reply_markup=get_main_menu_keyboard(),
            )
            return

        # Download photo
        file_data = await message.bot.download_file(file.file_path)

        # Convert to base64
        image_bytes = file_data.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # Process image with AI
        ai_service = AIService()
        result = await ai_service.process_image_text(
            image_base64=image_base64,
            user_prompt=user_prompt,
        )

        # Delete processing message
        try:
            await processing_msg.delete()
        except Exception as delete_error:
            logger.debug(f"Failed to delete processing message: {delete_error}")

        # Check if Greek text was found
        if not result.has_greek_text:
            await message.answer(
                photo_msg.MSG_NO_GREEK_TEXT,
                reply_markup=get_main_menu_keyboard(),
            )
            return

        # Extract vocabulary from recognized Greek text
        vocab_service = VocabularyExtractionService(session)
        extraction = await vocab_service.extract_vocabulary(
            user=user,
            phrase=result.recognized_text,
            phrase_translation=result.translation,
            source_language="greek",
        )

        # Format base response
        response = photo_msg.format_photo_result(
            recognized_text=result.recognized_text,
            translation=result.translation,
            prompt_response=result.additional_response,
        )

        # Determine keyboard and suffix based on vocabulary extraction
        keyboard: ReplyKeyboardMarkup | InlineKeyboardMarkup = get_main_menu_keyboard()
        extraction_suffix = ""

        if extraction.new_words:
            # Store extraction data in FSM state
            extraction_hash = create_callback_hash(result.recognized_text)
            words_data = [
                {
                    "original_form": w.original_form,
                    "lemma": w.lemma,
                    "lemma_with_article": w.lemma_with_article,
                    "translation": w.translation,
                    "part_of_speech": w.part_of_speech,
                    "already_in_cards": w.already_in_cards,
                }
                for w in extraction.new_words
            ]
            await state.update_data(
                extraction_hash=extraction_hash,
                extraction_words=json.dumps(words_data, ensure_ascii=False),
                source_language="greek",
            )
            keyboard = get_vocabulary_extraction_keyboard(extraction_hash)
            extraction_suffix = (
                f"\n\n{vocab_msg.MSG_VOCABULARY_FOUND.format(count=len(extraction.new_words))}"
            )
        elif extraction.existing_words:
            extraction_suffix = f"\n\n{vocab_msg.MSG_NO_NEW_WORDS}"

        # Add vocabulary info to response
        response += extraction_suffix

        # Handle long messages
        chunks = photo_msg.split_long_message(response)
        for i, chunk in enumerate(chunks):
            if i == len(chunks) - 1:
                # Last chunk gets the keyboard
                await message.answer(chunk, reply_markup=keyboard)
            else:
                await message.answer(chunk)

    except Exception as e:
        logger.exception(f"Photo processing failed: {e}")
        try:
            await processing_msg.delete()
        except Exception:
            pass
        await message.answer(
            photo_msg.MSG_PROCESSING_ERROR,
            reply_markup=get_main_menu_keyboard(),
        )
