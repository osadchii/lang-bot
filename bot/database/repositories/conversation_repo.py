"""Conversation message repository."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import CursorResult, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.conversation import ConversationMessage, MessageRole
from bot.database.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[ConversationMessage]):
    """Repository for ConversationMessage model."""

    def __init__(self, session: AsyncSession):
        """Initialize conversation repository.

        Args:
            session: Async database session
        """
        super().__init__(ConversationMessage, session)

    async def add_message(
        self,
        user_id: int,
        role: MessageRole,
        content: str,
        conversation_id: str = "default",
        message_type: str | None = None,
        token_count: int | None = None,
    ) -> ConversationMessage:
        """Add a new message to the conversation.

        Args:
            user_id: User's database ID
            role: Message role (user/assistant/system)
            content: Message content
            conversation_id: Conversation identifier
            message_type: Type of AI interaction
            token_count: Optional token count

        Returns:
            Created message instance
        """
        return await self.create(
            user_id=user_id,
            role=role.value,
            content=content,
            conversation_id=conversation_id,
            message_type=message_type,
            token_count=token_count,
        )

    async def get_recent_messages(
        self,
        user_id: int,
        conversation_id: str = "default",
        limit: int = 10,
    ) -> list[ConversationMessage]:
        """Get recent messages for a conversation.

        Args:
            user_id: User's database ID
            conversation_id: Conversation identifier
            limit: Maximum number of messages to return

        Returns:
            List of messages ordered by creation time (oldest first for API context)
        """
        query = (
            select(ConversationMessage)
            .where(
                ConversationMessage.user_id == user_id,
                ConversationMessage.conversation_id == conversation_id,
            )
            .order_by(ConversationMessage.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        messages = list(result.scalars().all())
        return list(reversed(messages))

    async def get_conversation_history(
        self,
        user_id: int,
        conversation_id: str = "default",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[ConversationMessage]:
        """Get full conversation history with pagination.

        Args:
            user_id: User's database ID
            conversation_id: Conversation identifier
            limit: Maximum number of messages
            offset: Number of messages to skip

        Returns:
            List of messages ordered chronologically
        """
        query = (
            select(ConversationMessage)
            .where(
                ConversationMessage.user_id == user_id,
                ConversationMessage.conversation_id == conversation_id,
            )
            .order_by(ConversationMessage.created_at.asc())
            .offset(offset)
        )
        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_messages(
        self,
        user_id: int,
        conversation_id: str = "default",
    ) -> int:
        """Count messages in a conversation.

        Args:
            user_id: User's database ID
            conversation_id: Conversation identifier

        Returns:
            Message count
        """
        query = (
            select(func.count())
            .select_from(ConversationMessage)
            .where(
                ConversationMessage.user_id == user_id,
                ConversationMessage.conversation_id == conversation_id,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def clear_conversation(
        self,
        user_id: int,
        conversation_id: str = "default",
    ) -> int:
        """Clear all messages in a conversation.

        Args:
            user_id: User's database ID
            conversation_id: Conversation identifier

        Returns:
            Number of messages deleted
        """
        query = delete(ConversationMessage).where(
            ConversationMessage.user_id == user_id,
            ConversationMessage.conversation_id == conversation_id,
        )
        cursor_result: CursorResult = await self.session.execute(query)  # type: ignore[assignment]
        await self.session.flush()
        return cursor_result.rowcount or 0

    async def delete_old_messages(
        self,
        days: int = 30,
    ) -> int:
        """Delete messages older than specified days (cleanup task).

        Args:
            days: Age threshold in days

        Returns:
            Number of messages deleted
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=days)

        query = delete(ConversationMessage).where(ConversationMessage.created_at < cutoff_date)
        cursor_result: CursorResult = await self.session.execute(query)  # type: ignore[assignment]
        await self.session.flush()
        return cursor_result.rowcount or 0

    async def get_user_conversations(
        self,
        user_id: int,
    ) -> list[str]:
        """Get all conversation IDs for a user.

        Args:
            user_id: User's database ID

        Returns:
            List of distinct conversation IDs
        """
        query = (
            select(ConversationMessage.conversation_id)
            .where(ConversationMessage.user_id == user_id)
            .distinct()
        )
        result = await self.session.execute(query)
        return [row[0] for row in result.fetchall()]
