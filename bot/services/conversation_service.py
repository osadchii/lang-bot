"""Conversation service for managing AI chat history."""

from sqlalchemy.ext.asyncio import AsyncSession

from bot.config.logging_config import get_logger
from bot.config.settings import settings
from bot.database.models.conversation import ConversationMessage, MessageRole
from bot.database.models.user import User
from bot.database.repositories.conversation_repo import ConversationRepository

logger = get_logger(__name__)


class ConversationService:
    """Service for managing conversation history."""

    def __init__(self, session: AsyncSession):
        """Initialize conversation service.

        Args:
            session: Async database session
        """
        self.session = session
        self.repo = ConversationRepository(session)

    async def add_user_message(
        self,
        user: User,
        content: str,
        conversation_id: str = "default",
        message_type: str | None = None,
    ) -> ConversationMessage:
        """Add a user message to the conversation.

        Args:
            user: User model instance
            content: Message content
            conversation_id: Conversation identifier
            message_type: Type of interaction (ask_question, translate, etc.)

        Returns:
            Created message instance
        """
        logger.debug(
            f"Adding user message for user_id={user.id}, "
            f"conversation_id={conversation_id}, type={message_type}"
        )
        return await self.repo.add_message(
            user_id=user.id,
            role=MessageRole.USER,
            content=content,
            conversation_id=conversation_id,
            message_type=message_type,
        )

    async def add_assistant_message(
        self,
        user: User,
        content: str,
        conversation_id: str = "default",
        message_type: str | None = None,
        token_count: int | None = None,
    ) -> ConversationMessage:
        """Add an assistant (AI) message to the conversation.

        Args:
            user: User model instance
            content: Message content
            conversation_id: Conversation identifier
            message_type: Type of interaction
            token_count: Optional token usage

        Returns:
            Created message instance
        """
        logger.debug(
            f"Adding assistant message for user_id={user.id}, " f"conversation_id={conversation_id}"
        )
        return await self.repo.add_message(
            user_id=user.id,
            role=MessageRole.ASSISTANT,
            content=content,
            conversation_id=conversation_id,
            message_type=message_type,
            token_count=token_count,
        )

    async def get_context_messages(
        self,
        user: User,
        conversation_id: str = "default",
        limit: int | None = None,
    ) -> list[dict[str, str]]:
        """Get recent messages formatted for OpenAI API.

        Args:
            user: User model instance
            conversation_id: Conversation identifier
            limit: Number of messages (uses setting if not provided)

        Returns:
            List of message dicts with 'role' and 'content' keys
        """
        message_limit = limit or settings.conversation_history_limit

        messages = await self.repo.get_recent_messages(
            user_id=user.id,
            conversation_id=conversation_id,
            limit=message_limit,
        )

        return [{"role": msg.role, "content": msg.content} for msg in messages]

    async def clear_conversation(
        self,
        user: User,
        conversation_id: str = "default",
    ) -> int:
        """Clear conversation history for a user.

        Args:
            user: User model instance
            conversation_id: Conversation identifier

        Returns:
            Number of messages deleted
        """
        logger.info(
            f"Clearing conversation for user_id={user.id}, " f"conversation_id={conversation_id}"
        )
        return await self.repo.clear_conversation(
            user_id=user.id,
            conversation_id=conversation_id,
        )

    async def get_conversation_stats(
        self,
        user: User,
        conversation_id: str = "default",
    ) -> dict[str, int]:
        """Get conversation statistics.

        Args:
            user: User model instance
            conversation_id: Conversation identifier

        Returns:
            Dictionary with message counts
        """
        total = await self.repo.count_messages(
            user_id=user.id,
            conversation_id=conversation_id,
        )
        return {"total_messages": total}

    async def cleanup_old_messages(
        self,
        days: int | None = None,
    ) -> int:
        """Cleanup old messages across all users.

        Args:
            days: Age threshold (uses setting if not provided)

        Returns:
            Number of messages deleted
        """
        retention_days = days or settings.conversation_retention_days
        deleted = await self.repo.delete_old_messages(days=retention_days)
        logger.info(f"Cleaned up {deleted} old conversation messages")
        return deleted
