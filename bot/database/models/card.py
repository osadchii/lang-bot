"""Card model with spaced repetition data."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from bot.database.models.deck import Deck
    from bot.database.models.review import Review


class Card(Base, TimestampMixin):
    """Flashcard model with SRS (Spaced Repetition System) data."""

    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    deck_id: Mapped[int] = mapped_column(ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)

    # Card content
    front: Mapped[str] = mapped_column(Text, nullable=False)  # Greek word/phrase
    back: Mapped[str] = mapped_column(Text, nullable=False)  # Translation
    example: Mapped[str | None] = mapped_column(Text, nullable=True)  # Example sentence
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)  # Additional notes

    # Spaced Repetition System (SRS) fields - SM-2 algorithm
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    interval: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Days
    repetitions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_review: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )

    # Learning statistics
    total_reviews: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    correct_reviews: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Table arguments for composite indexes
    __table_args__ = (
        Index("ix_cards_deck_next_review", "deck_id", "next_review"),
        Index("ix_cards_deck_repetitions", "deck_id", "repetitions"),
    )

    # Relationships
    deck: Mapped[Deck] = relationship("Deck", back_populates="cards")
    reviews: Mapped[list[Review]] = relationship(
        "Review", back_populates="card", cascade="all, delete-orphan"
    )

    @property
    def success_rate(self) -> float:
        """Calculate the success rate of this card.

        Returns:
            Success rate as a percentage (0.0 to 100.0)
        """
        if self.total_reviews == 0:
            return 0.0
        return (self.correct_reviews / self.total_reviews) * 100

    @property
    def is_due(self) -> bool:
        """Check if the card is due for review.

        Returns:
            True if the card should be reviewed now
        """
        return datetime.now(UTC) >= self.next_review

    def __repr__(self) -> str:
        return (
            f"<Card(id={self.id}, front={self.front[:20]}, "
            f"next_review={self.next_review}, interval={self.interval})>"
        )
