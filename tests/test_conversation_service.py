"""Tests for conversation service."""

import pytest

from bot.database.models.user import User
from bot.services.conversation_service import ConversationService


@pytest.fixture
async def sample_user(db_session, sample_user_data) -> User:
    """Create a sample user for testing."""
    user = User(**sample_user_data)
    db_session.add(user)
    await db_session.flush()
    return user


class TestConversationService:
    """Tests for ConversationService."""

    @pytest.mark.asyncio
    async def test_add_user_message(self, db_session, sample_user):
        """Test adding a user message."""
        service = ConversationService(db_session)
        msg = await service.add_user_message(sample_user, "Hello!")

        assert msg.id is not None
        assert msg.content == "Hello!"
        assert msg.role == "user"

    @pytest.mark.asyncio
    async def test_add_assistant_message(self, db_session, sample_user):
        """Test adding an assistant message."""
        service = ConversationService(db_session)
        msg = await service.add_assistant_message(
            sample_user, "Hi! How can I help?", message_type="ask_question"
        )

        assert msg.id is not None
        assert msg.content == "Hi! How can I help?"
        assert msg.role == "assistant"
        assert msg.message_type == "ask_question"

    @pytest.mark.asyncio
    async def test_get_context_messages_format(self, db_session, sample_user):
        """Test that context messages are formatted correctly for OpenAI API."""
        service = ConversationService(db_session)

        await service.add_user_message(sample_user, "What is hello in Greek?")
        await service.add_assistant_message(sample_user, "Hello in Greek is: Γεια σου")

        context = await service.get_context_messages(sample_user)

        assert len(context) == 2
        assert context[0] == {"role": "user", "content": "What is hello in Greek?"}
        assert context[1] == {"role": "assistant", "content": "Hello in Greek is: Γεια σου"}

    @pytest.mark.asyncio
    async def test_context_limit(self, db_session, sample_user):
        """Test that context respects the limit parameter."""
        service = ConversationService(db_session)

        for i in range(15):
            await service.add_user_message(sample_user, f"Message {i}")

        context = await service.get_context_messages(sample_user, limit=10)
        assert len(context) == 10
        assert context[0]["content"] == "Message 5"
        assert context[9]["content"] == "Message 14"

    @pytest.mark.asyncio
    async def test_clear_conversation(self, db_session, sample_user):
        """Test clearing conversation history."""
        service = ConversationService(db_session)

        await service.add_user_message(sample_user, "Test 1")
        await service.add_assistant_message(sample_user, "Response 1")
        await service.add_user_message(sample_user, "Test 2")

        deleted = await service.clear_conversation(sample_user)
        assert deleted == 3

        context = await service.get_context_messages(sample_user)
        assert len(context) == 0

    @pytest.mark.asyncio
    async def test_get_conversation_stats(self, db_session, sample_user):
        """Test getting conversation statistics."""
        service = ConversationService(db_session)

        await service.add_user_message(sample_user, "Question 1")
        await service.add_assistant_message(sample_user, "Answer 1")
        await service.add_user_message(sample_user, "Question 2")

        stats = await service.get_conversation_stats(sample_user)
        assert stats["total_messages"] == 3

    @pytest.mark.asyncio
    async def test_empty_history_returns_empty_list(self, db_session, sample_user):
        """Test that empty history returns empty list."""
        service = ConversationService(db_session)

        context = await service.get_context_messages(sample_user)
        assert context == []

    @pytest.mark.asyncio
    async def test_separate_conversation_ids(self, db_session, sample_user):
        """Test that different conversation IDs are isolated."""
        service = ConversationService(db_session)

        await service.add_user_message(sample_user, "Conv 1 message", conversation_id="conv1")
        await service.add_user_message(sample_user, "Conv 2 message", conversation_id="conv2")

        context1 = await service.get_context_messages(sample_user, conversation_id="conv1")
        context2 = await service.get_context_messages(sample_user, conversation_id="conv2")

        assert len(context1) == 1
        assert len(context2) == 1
        assert context1[0]["content"] == "Conv 1 message"
        assert context2[0]["content"] == "Conv 2 message"
