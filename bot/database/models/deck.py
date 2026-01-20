"""Deck model for organizing cards."""

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.base import Base, TimestampMixin


class Deck(Base, TimestampMixin):
    """Deck model for grouping cards."""

    __tablename__ = "decks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Table arguments for constraints
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_deck_name"),)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="decks")
    cards: Mapped[list["Card"]] = relationship(
        "Card", back_populates="deck", cascade="all, delete-orphan"
    )
    learning_stats: Mapped[list["LearningStats"]] = relationship(
        "LearningStats", back_populates="deck", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Deck(id={self.id}, name={self.name}, user_id={self.user_id})>"
