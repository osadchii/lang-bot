"""Statistics and progress tracking handlers."""

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.user import User
from bot.services.statistics_service import StatisticsService
from bot.telegram.keyboards.main_menu import get_back_to_menu_keyboard

router = Router(name="statistics")


@router.message(F.text == "📊 Statistics")
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

    # Format time
    def format_time(seconds: int) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    text = (
        "📊 <b>Your Learning Statistics</b>\n\n"
        "<b>📈 Overall:</b>\n"
        f"• Total Reviews: {overall['total_reviews']}\n"
        f"• Accuracy: {overall['accuracy']:.1f}%\n"
        f"• Total Study Time: {format_time(overall['total_time_seconds'])}\n"
        f"• Current Streak: {overall['current_streak']} days 🔥\n"
        f"• Days Active: {overall['total_days_active']}\n\n"
        "<b>📅 Today:</b>\n"
        f"• Reviews: {daily['total_reviews']}\n"
        f"• Accuracy: {daily['accuracy']:.1f}%\n"
        f"• Study Time: {format_time(daily['total_time_seconds'])}\n\n"
        "<b>📆 This Week:</b>\n"
        f"• Total Reviews: {weekly['total_reviews']}\n"
        f"• Avg Daily Reviews: {weekly['average_daily_reviews']:.1f}\n"
        f"• Days Active: {weekly['days_active']}/7\n"
        f"• Study Time: {format_time(weekly['total_time_seconds'])}"
    )

    keyboard = get_back_to_menu_keyboard()

    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard)
    else:
        await event.message.edit_text(text, reply_markup=keyboard)
        await event.answer()
