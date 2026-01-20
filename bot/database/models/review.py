"""Review history model."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.base import Base

if TYPE_CHECKING:
    from bot.database.models.card import Card
    from bot.database.models.user import User


class Review(Base):
    """Review history for tracking card performance."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Review data
    quality: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("quality IN (0, 2, 3, 5)", name="check_quality_values"),
        nullable=False,
    )  # 0=Again, 2=Hard, 3=Good, 5=Easy
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )
    time_spent: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Time spent in seconds

    # SRS state at time of review (for analytics)
    ease_factor_before: Mapped[float | None] = mapped_column(nullable=True)
    interval_before: Mapped[int | None] = mapped_column(nullable=True)

    # Table arguments for indexes
    __table_args__ = (Index("ix_reviews_user_date", "user_id", "reviewed_at"),)

    # Relationships
    card: Mapped[Card] = relationship("Card", back_populates="reviews")
    user: Mapped[User] = relationship("User", back_populates="reviews")

    def __repr__(self) -> str:
        return (
            f"<Review(id={self.id}, card_id={self.card_id}, "
            f"quality={self.quality}, reviewed_at={self.reviewed_at})>"
        )
