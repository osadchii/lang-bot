"""Review repository."""

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.review import Review
from bot.database.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    """Repository for Review model."""

    def __init__(self, session: AsyncSession):
        """Initialize review repository.

        Args:
            session: Async database session
        """
        super().__init__(Review, session)

    async def get_card_reviews(self, card_id: int, limit: int | None = None) -> list[Review]:
        """Get all reviews for a card.

        Args:
            card_id: Card ID
            limit: Maximum number of reviews to return

        Returns:
            List of review instances, ordered by date (newest first)
        """
        query = select(Review).where(Review.card_id == card_id).order_by(Review.reviewed_at.desc())

        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_user_reviews(
        self,
        user_id: int,
        limit: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[Review]:
        """Get all reviews for a user.

        Args:
            user_id: User ID
            limit: Maximum number of reviews to return
            start_date: Filter reviews after this date
            end_date: Filter reviews before this date

        Returns:
            List of review instances, ordered by date (newest first)
        """
        query = select(Review).where(Review.user_id == user_id)

        if start_date:
            query = query.where(Review.reviewed_at >= start_date)
        if end_date:
            query = query.where(Review.reviewed_at <= end_date)

        query = query.order_by(Review.reviewed_at.desc())

        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_daily_review_count(self, user_id: int, target_date: date | None = None) -> int:
        """Get number of reviews for a specific day.

        Args:
            user_id: User ID
            target_date: Target date (defaults to today)

        Returns:
            Number of reviews
        """
        if target_date is None:
            target_date = date.today()

        start_of_day = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=UTC)
        end_of_day = start_of_day + timedelta(days=1)

        query = (
            select(func.count())
            .select_from(Review)
            .where(
                Review.user_id == user_id,
                Review.reviewed_at >= start_of_day,
                Review.reviewed_at < end_of_day,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_review_streak(self, user_id: int) -> int:
        """Calculate user's current review streak in days.

        Args:
            user_id: User ID

        Returns:
            Streak count in days
        """
        # Get all unique review dates
        query = (
            select(func.date(Review.reviewed_at))
            .where(Review.user_id == user_id)
            .distinct()
            .order_by(func.date(Review.reviewed_at).desc())
        )
        result = await self.session.execute(query)
        review_dates = [row[0] for row in result.all()]

        if not review_dates:
            return 0

        # Calculate streak
        today = date.today()
        streak = 0

        # Check if user reviewed today or yesterday (streak continues)
        if review_dates[0] not in (today, today - timedelta(days=1)):
            return 0

        current_date = review_dates[0]
        for review_date in review_dates:
            if (current_date - review_date).days <= 1:
                streak += 1
                current_date = review_date
            else:
                break

        return streak
