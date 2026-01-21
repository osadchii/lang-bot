"""Conversation message model for AI chat history."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from bot.database.models.user import User


class MessageRole(str, Enum):
    """Role of the message sender."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationMessage(Base, TimestampMixin):
    """AI conversation message model.

    Stores individual messages in the conversation between user and AI.
    """

    __tablename__ = "conversation_messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    conversation_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        default="default",
    )

    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    message_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    token_count: Mapped[int | None] = mapped_column(nullable=True)

    user: Mapped[User] = relationship("User", back_populates="conversation_messages")

    def __repr__(self) -> str:
        return (
            f"<ConversationMessage(id={self.id}, user_id={self.user_id}, "
            f"role={self.role}, content_len={len(self.content)})>"
        )
