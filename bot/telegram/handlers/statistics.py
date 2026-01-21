"""Statistics and progress tracking handlers."""

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.user import User
from bot.messages import common as common_msg
from bot.messages import statistics as stats_msg
from bot.services.statistics_service import StatisticsService
from bot.telegram.keyboards.main_menu import get_back_to_menu_keyboard

router = Router(name="statistics")


@router.message(F.text == common_msg.BTN_STATISTICS)
@router.callback_query(F.data == "statistics")
async def show_statistics(event: Message | CallbackQuery, session: AsyncSession, user: User):
    """Show user statistics.

    Args:
        event: Message or callback query
        session: Database session
        user: User instance
    """
    stats_service = StatisticsService(session)

    # Get overall stats
    overall = await stats_service.get_overall_stats(user.id)

    # Get daily stats
    daily = await stats_service.get_daily_stats(user.id)

    # Get weekly stats
    weekly = await stats_service.get_weekly_stats(user.id)

    text = stats_msg.get_statistics_message(
        total_reviews=overall["total_reviews"],
        accuracy=overall["accuracy"],
        total_time_seconds=overall["total_time_seconds"],
        current_streak=overall["current_streak"],
        total_days_active=overall["total_days_active"],
        daily_reviews=daily["total_reviews"],
        daily_accuracy=daily["accuracy"],
        daily_time_seconds=daily["total_time_seconds"],
        weekly_reviews=weekly["total_reviews"],
        weekly_avg_daily=weekly["average_daily_reviews"],
        weekly_days_active=weekly["days_active"],
        weekly_time_seconds=weekly["total_time_seconds"],
    )

    keyboard = get_back_to_menu_keyboard()

    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard)
    else:
        await event.message.edit_text(text, reply_markup=keyboard)
        await event.answer()
