"""Statistics messages in Russian."""


def format_time(seconds: int) -> str:
    """Format seconds into human readable time.

    Args:
        seconds: Total seconds

    Returns:
        Formatted time string
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}ч {minutes}мин"
    return f"{minutes}мин"


def get_statistics_message(
    total_reviews: int,
    accuracy: float,
    total_time_seconds: int,
    current_streak: int,
    total_days_active: int,
    daily_reviews: int,
    daily_accuracy: float,
    daily_time_seconds: int,
    weekly_reviews: int,
    weekly_avg_daily: float,
    weekly_days_active: int,
    weekly_time_seconds: int,
) -> str:
    """Get full statistics message.

    Args:
        total_reviews: Total number of reviews
        accuracy: Overall accuracy percentage
        total_time_seconds: Total study time in seconds
        current_streak: Current streak in days
        total_days_active: Total days active
        daily_reviews: Today's reviews
        daily_accuracy: Today's accuracy
        daily_time_seconds: Today's study time
        weekly_reviews: This week's reviews
        weekly_avg_daily: Average daily reviews this week
        weekly_days_active: Days active this week
        weekly_time_seconds: Study time this week

    Returns:
        Formatted statistics message
    """
    return (
        "<b>Твоя статистика обучения</b>\n\n"
        "<b>Всего:</b>\n"
        f"- Повторений: {total_reviews}\n"
        f"- Точность: {accuracy:.1f}%\n"
        f"- Время обучения: {format_time(total_time_seconds)}\n"
        f"- Текущая серия: {current_streak} дней\n"
        f"- Дней активности: {total_days_active}\n\n"
        "<b>Сегодня:</b>\n"
        f"- Повторений: {daily_reviews}\n"
        f"- Точность: {daily_accuracy:.1f}%\n"
        f"- Время обучения: {format_time(daily_time_seconds)}\n\n"
        "<b>На этой неделе:</b>\n"
        f"- Всего повторений: {weekly_reviews}\n"
        f"- В среднем в день: {weekly_avg_daily:.1f}\n"
        f"- Дней активности: {weekly_days_active}/7\n"
        f"- Время обучения: {format_time(weekly_time_seconds)}"
    )
