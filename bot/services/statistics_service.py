"""Statistics service for tracking learning progress."""

from datetime import UTC, date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repositories.card_repo import CardRepository
from bot.database.repositories.review_repo import ReviewRepository


class StatisticsService:
    """Service for learning statistics."""

    def __init__(self, session: AsyncSession):
        """Initialize statistics service.

        Args:
            session: Async database session
        """
        self.card_repo = CardRepository(session)
        self.review_repo = ReviewRepository(session)

    async def get_daily_stats(self, user_id: int, target_date: date | None = None) -> dict:
        """Get statistics for a specific day.

        Args:
            user_id: User ID
            target_date: Target date (defaults to today)

        Returns:
            Dictionary with daily statistics
        """
        if target_date is None:
            target_date = date.today()

        # Get reviews for the day
        start_of_day = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=UTC)
        end_of_day = start_of_day + timedelta(days=1)

        reviews = await self.review_repo.get_user_reviews(
            user_id=user_id, start_date=start_of_day, end_date=end_of_day
        )

        total_reviews = len(reviews)
        correct_reviews = sum(1 for r in reviews if r.quality >= 3)
        total_time = sum(r.time_spent or 0 for r in reviews)

        accuracy = (correct_reviews / total_reviews * 100) if total_reviews > 0 else 0

        return {
            "date": target_date,
            "total_reviews": total_reviews,
            "correct_reviews": correct_reviews,
            "accuracy": round(accuracy, 1),
            "total_time_seconds": total_time,
        }

    async def get_weekly_stats(self, user_id: int) -> dict:
        """Get statistics for the past week.

        Args:
            user_id: User ID

        Returns:
            Dictionary with weekly statistics
        """
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=7)

        reviews = await self.review_repo.get_user_reviews(
            user_id=user_id, start_date=start_date, end_date=end_date
        )

        total_reviews = len(reviews)
        correct_reviews = sum(1 for r in reviews if r.quality >= 3)
        total_time = sum(r.time_spent or 0 for r in reviews)

        # Group by day
        daily_counts: dict[date, int] = {}
        for review in reviews:
            review_date = review.reviewed_at.date()
            daily_counts[review_date] = daily_counts.get(review_date, 0) + 1

        avg_daily_reviews = total_reviews / 7 if total_reviews > 0 else 0

        return {
            "period_days": 7,
            "total_reviews": total_reviews,
            "correct_reviews": correct_reviews,
            "average_daily_reviews": round(avg_daily_reviews, 1),
            "total_time_seconds": total_time,
            "days_active": len(daily_counts),
        }

    async def get_user_streak(self, user_id: int) -> int:
        """Get user's current learning streak.

        Args:
            user_id: User ID

        Returns:
            Streak count in days
        """
        return await self.review_repo.get_review_streak(user_id)

    async def get_deck_progress(self, deck_id: int) -> dict:
        """Get progress statistics for a deck.

        Args:
            deck_id: Deck ID

        Returns:
            Dictionary with deck progress statistics
        """
        all_cards = await self.card_repo.get_deck_cards(deck_id)

        if not all_cards:
            return {
                "total_cards": 0,
                "new_cards": 0,
                "learning_cards": 0,
                "mastered_cards": 0,
                "average_success_rate": 0,
            }

        new_cards = sum(1 for c in all_cards if c.repetitions == 0)
        learning_cards = sum(1 for c in all_cards if 0 < c.repetitions < 5)
        mastered_cards = sum(1 for c in all_cards if c.repetitions >= 5)

        # Calculate average success rate
        cards_with_reviews = [c for c in all_cards if c.total_reviews > 0]
        if cards_with_reviews:
            avg_success_rate = sum(c.success_rate for c in cards_with_reviews) / len(
                cards_with_reviews
            )
        else:
            avg_success_rate = 0

        return {
            "total_cards": len(all_cards),
            "new_cards": new_cards,
            "learning_cards": learning_cards,
            "mastered_cards": mastered_cards,
            "average_success_rate": round(avg_success_rate, 1),
        }

    async def get_overall_stats(self, user_id: int) -> dict:
        """Get overall statistics for a user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with overall statistics
        """
        all_reviews = await self.review_repo.get_user_reviews(user_id=user_id)

        total_reviews = len(all_reviews)
        correct_reviews = sum(1 for r in all_reviews if r.quality >= 3)
        total_time = sum(r.time_spent or 0 for r in all_reviews)
        streak = await self.get_user_streak(user_id)

        accuracy = (correct_reviews / total_reviews * 100) if total_reviews > 0 else 0

        # Get unique review dates
        unique_dates = set(r.reviewed_at.date() for r in all_reviews)

        return {
            "total_reviews": total_reviews,
            "correct_reviews": correct_reviews,
            "accuracy": round(accuracy, 1),
            "total_time_seconds": total_time,
            "current_streak": streak,
            "total_days_active": len(unique_dates),
        }
