"""Learning statistics model."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from bot.database.models.deck import Deck
    from bot.database.models.user import User


class LearningStats(Base, TimestampMixin):
    """Daily learning statistics per deck."""

    __tablename__ = "learning_stats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    deck_id: Mapped[int] = mapped_column(ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False, index=True)

    # Daily statistics
    cards_reviewed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cards_learned: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )  # New cards learned
    correct_answers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_answers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    time_spent: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )  # Total time in seconds

    # Streak tracking
    streak_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Table arguments for constraints and indexes
    __table_args__ = (
        UniqueConstraint("user_id", "deck_id", "date", name="uq_user_deck_date"),
        Index("ix_learning_stats_user_deck_date", "user_id", "deck_id", "date"),
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="learning_stats")
    deck: Mapped[Deck] = relationship("Deck", back_populates="learning_stats")

    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage for the day.

        Returns:
            Accuracy as a percentage (0.0 to 100.0)
        """
        if self.total_answers == 0:
            return 0.0
        return (self.correct_answers / self.total_answers) * 100

    def __repr__(self) -> str:
        return (
            f"<LearningStats(id={self.id}, user_id={self.user_id}, "
            f"date={self.date}, cards_reviewed={self.cards_reviewed})>"
        )
