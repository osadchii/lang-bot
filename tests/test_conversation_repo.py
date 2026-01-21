"""Tests for conversation repository."""

import pytest

from bot.database.models.conversation import MessageRole
from bot.database.models.user import User
from bot.database.repositories.conversation_repo import ConversationRepository


@pytest.fixture
async def sample_user(db_session, sample_user_data) -> User:
    """Create a sample user for testing."""
    user = User(**sample_user_data)
    db_session.add(user)
    await db_session.flush()
    return user


class TestConversationRepository:
    """Tests for ConversationRepository."""

    @pytest.mark.asyncio
    async def test_add_message(self, db_session, sample_user):
        """Test adding a message to conversation."""
        repo = ConversationRepository(db_session)
        msg = await repo.add_message(
            user_id=sample_user.id,
            role=MessageRole.USER,
            content="Test message",
        )
        assert msg.id is not None
        assert msg.content == "Test message"
        assert msg.role == MessageRole.USER.value
        assert msg.conversation_id == "default"

    @pytest.mark.asyncio
    async def test_add_message_with_custom_conversation_id(self, db_session, sample_user):
        """Test adding a message with custom conversation ID."""
        repo = ConversationRepository(db_session)
        msg = await repo.add_message(
            user_id=sample_user.id,
            role=MessageRole.ASSISTANT,
            content="Custom conversation",
            conversation_id="custom_id",
            message_type="ask_question",
        )
        assert msg.conversation_id == "custom_id"
        assert msg.message_type == "ask_question"

    @pytest.mark.asyncio
    async def test_get_recent_messages_order(self, db_session, sample_user):
        """Test that recent messages are returned in chronological order."""
        repo = ConversationRepository(db_session)

        await repo.add_message(user_id=sample_user.id, role=MessageRole.USER, content="First")
        await repo.add_message(user_id=sample_user.id, role=MessageRole.ASSISTANT, content="Second")
        await repo.add_message(user_id=sample_user.id, role=MessageRole.USER, content="Third")

        messages = await repo.get_recent_messages(user_id=sample_user.id, limit=10)
        assert len(messages) == 3
        assert messages[0].content == "First"
        assert messages[1].content == "Second"
        assert messages[2].content == "Third"

    @pytest.mark.asyncio
    async def test_get_recent_messages_limit(self, db_session, sample_user):
        """Test that limit is respected for recent messages."""
        repo = ConversationRepository(db_session)

        for i in range(15):
            await repo.add_message(
                user_id=sample_user.id,
                role=MessageRole.USER,
                content=f"Message {i}",
            )

        messages = await repo.get_recent_messages(user_id=sample_user.id, limit=10)
        assert len(messages) == 10
        assert messages[0].content == "Message 5"
        assert messages[9].content == "Message 14"

    @pytest.mark.asyncio
    async def test_count_messages(self, db_session, sample_user):
        """Test counting messages in conversation."""
        repo = ConversationRepository(db_session)

        await repo.add_message(user_id=sample_user.id, role=MessageRole.USER, content="Test 1")
        await repo.add_message(user_id=sample_user.id, role=MessageRole.ASSISTANT, content="Test 2")

        count = await repo.count_messages(user_id=sample_user.id)
        assert count == 2

    @pytest.mark.asyncio
    async def test_clear_conversation(self, db_session, sample_user):
        """Test clearing conversation history."""
        repo = ConversationRepository(db_session)

        await repo.add_message(user_id=sample_user.id, role=MessageRole.USER, content="Test")
        await repo.add_message(
            user_id=sample_user.id, role=MessageRole.ASSISTANT, content="Response"
        )

        deleted = await repo.clear_conversation(user_id=sample_user.id)
        assert deleted == 2

        messages = await repo.get_recent_messages(user_id=sample_user.id)
        assert len(messages) == 0

    @pytest.mark.asyncio
    async def test_separate_conversations(self, db_session, sample_user):
        """Test that separate conversation IDs are isolated."""
        repo = ConversationRepository(db_session)

        await repo.add_message(
            user_id=sample_user.id,
            role=MessageRole.USER,
            content="Conv 1",
            conversation_id="conv1",
        )
        await repo.add_message(
            user_id=sample_user.id,
            role=MessageRole.USER,
            content="Conv 2",
            conversation_id="conv2",
        )

        messages_conv1 = await repo.get_recent_messages(
            user_id=sample_user.id, conversation_id="conv1"
        )
        messages_conv2 = await repo.get_recent_messages(
            user_id=sample_user.id, conversation_id="conv2"
        )

        assert len(messages_conv1) == 1
        assert len(messages_conv2) == 1
        assert messages_conv1[0].content == "Conv 1"
        assert messages_conv2[0].content == "Conv 2"

    @pytest.mark.asyncio
    async def test_get_user_conversations(self, db_session, sample_user):
        """Test getting all conversation IDs for a user."""
        repo = ConversationRepository(db_session)

        await repo.add_message(
            user_id=sample_user.id,
            role=MessageRole.USER,
            content="Test",
            conversation_id="conv1",
        )
        await repo.add_message(
            user_id=sample_user.id,
            role=MessageRole.USER,
            content="Test",
            conversation_id="conv2",
        )
        await repo.add_message(
            user_id=sample_user.id,
            role=MessageRole.USER,
            content="Test",
            conversation_id="conv1",
        )

        conversations = await repo.get_user_conversations(user_id=sample_user.id)
        assert len(conversations) == 2
        assert set(conversations) == {"conv1", "conv2"}
