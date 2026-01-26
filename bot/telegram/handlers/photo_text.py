"""Handler for photo messages with Greek text recognition."""

import base64

from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config.logging_config import get_logger
from bot.config.settings import settings
from bot.database.models.user import User
from bot.messages import photo_text as photo_msg
from bot.services.ai_service import AIService
from bot.telegram.keyboards.main_menu import get_main_menu_keyboard

logger = get_logger(__name__)

router = Router(name="photo_text")


@router.message(F.photo)
async def handle_photo(
    message: Message,
    session: AsyncSession,
    user: User,
    user_created: bool,
):
    """Handle photo messages for Greek text recognition.

    Uses OpenAI Vision API to recognize Greek text from photos
    and process it according to user's caption (if provided).

    Args:
        message: Message with photo
        session: Database session (unused but required by middleware)
        user: User instance (unused but required by middleware)
        user_created: Whether user was just created (unused)
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

        # Format and send response
        response = photo_msg.format_photo_result(
            recognized_text=result.recognized_text,
            translation=result.translation,
            prompt_response=result.additional_response,
        )

        # Handle long messages
        chunks = photo_msg.split_long_message(response)
        for i, chunk in enumerate(chunks):
            if i == len(chunks) - 1:
                # Last chunk gets the keyboard
                await message.answer(chunk, reply_markup=get_main_menu_keyboard())
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
