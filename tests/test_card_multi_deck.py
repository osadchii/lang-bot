"""Tests for card multi-deck query functionality."""

from datetime import UTC, datetime, timedelta

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.deck import Deck
from bot.database.models.user import User
from bot.database.repositories.card_repo import CardRepository
from bot.database.repositories.deck_repo import DeckRepository
from bot.database.repositories.user_repo import UserRepository


@pytest_asyncio.fixture
async def user(db_session: AsyncSession, sample_user_data: dict) -> User:
    """Create a user for testing."""
    user_repo = UserRepository(db_session)
    return await user_repo.create(**sample_user_data)


@pytest_asyncio.fixture
async def deck1(db_session: AsyncSession, user: User) -> Deck:
    """Create first deck for testing."""
    deck_repo = DeckRepository(db_session)
    return await deck_repo.create(
        user_id=user.id,
        name="Deck 1",
        is_active=True,
    )


@pytest_asyncio.fixture
async def deck2(db_session: AsyncSession, user: User) -> Deck:
    """Create second deck for testing."""
    deck_repo = DeckRepository(db_session)
    return await deck_repo.create(
        user_id=user.id,
        name="Deck 2",
        is_active=True,
    )


class TestCardMultiDeckQueries:
    """Tests for multi-deck card queries."""

    async def test_get_due_cards_from_decks_empty_list(self, db_session: AsyncSession):
        """Test that empty deck list returns empty result."""
        card_repo = CardRepository(db_session)
        cards = await card_repo.get_due_cards_from_decks([])
        assert cards == []

    async def test_get_new_cards_from_decks_empty_list(self, db_session: AsyncSession):
        """Test that empty deck list returns empty result."""
        card_repo = CardRepository(db_session)
        cards = await card_repo.get_new_cards_from_decks([])
        assert cards == []

    async def test_count_due_cards_from_decks_empty_list(self, db_session: AsyncSession):
        """Test that empty deck list returns zero count."""
        card_repo = CardRepository(db_session)
        count = await card_repo.count_due_cards_from_decks([])
        assert count == 0

    async def test_count_new_cards_from_decks_empty_list(self, db_session: AsyncSession):
        """Test that empty deck list returns zero count."""
        card_repo = CardRepository(db_session)
        count = await card_repo.count_new_cards_from_decks([])
        assert count == 0

    async def test_get_new_cards_from_multiple_decks(
        self, db_session: AsyncSession, deck1: Deck, deck2: Deck
    ):
        """Test getting new cards from multiple decks."""
        card_repo = CardRepository(db_session)

        # Create new cards in both decks
        card1 = await card_repo.create(
            deck_id=deck1.id,
            front="Word 1",
            back="Translation 1",
            repetitions=0,  # New card
        )
        card2 = await card_repo.create(
            deck_id=deck2.id,
            front="Word 2",
            back="Translation 2",
            repetitions=0,  # New card
        )

        new_cards = await card_repo.get_new_cards_from_decks([deck1.id, deck2.id])

        assert len(new_cards) == 2
        card_ids = [c.id for c in new_cards]
        assert card1.id in card_ids
        assert card2.id in card_ids

    async def test_get_due_cards_from_multiple_decks(
        self, db_session: AsyncSession, deck1: Deck, deck2: Deck
    ):
        """Test getting due cards from multiple decks."""
        card_repo = CardRepository(db_session)
        past_time = datetime.now(UTC) - timedelta(days=1)

        # Create due cards in both decks
        card1 = await card_repo.create(
            deck_id=deck1.id,
            front="Word 1",
            back="Translation 1",
            repetitions=1,
            next_review=past_time,
        )
        card2 = await card_repo.create(
            deck_id=deck2.id,
            front="Word 2",
            back="Translation 2",
            repetitions=1,
            next_review=past_time,
        )

        due_cards = await card_repo.get_due_cards_from_decks([deck1.id, deck2.id])

        assert len(due_cards) == 2
        card_ids = [c.id for c in due_cards]
        assert card1.id in card_ids
        assert card2.id in card_ids

    async def test_get_due_cards_sorted_by_next_review(
        self, db_session: AsyncSession, deck1: Deck, deck2: Deck
    ):
        """Test that due cards are sorted by next_review (oldest first)."""
        card_repo = CardRepository(db_session)

        # Create cards with different review times
        older_time = datetime.now(UTC) - timedelta(days=5)
        newer_time = datetime.now(UTC) - timedelta(days=1)

        card_newer = await card_repo.create(
            deck_id=deck1.id,
            front="Newer Card",
            back="Translation",
            repetitions=1,
            next_review=newer_time,
        )
        card_older = await card_repo.create(
            deck_id=deck2.id,
            front="Older Card",
            back="Translation",
            repetitions=1,
            next_review=older_time,
        )

        due_cards = await card_repo.get_due_cards_from_decks([deck1.id, deck2.id])

        assert len(due_cards) == 2
        # Older card should be first
        assert due_cards[0].id == card_older.id
        assert due_cards[1].id == card_newer.id

    async def test_count_new_cards_from_multiple_decks(
        self, db_session: AsyncSession, deck1: Deck, deck2: Deck
    ):
        """Test counting new cards from multiple decks."""
        card_repo = CardRepository(db_session)

        # Create new cards in both decks
        await card_repo.create(
            deck_id=deck1.id,
            front="Word 1",
            back="Translation 1",
            repetitions=0,
        )
        await card_repo.create(
            deck_id=deck1.id,
            front="Word 2",
            back="Translation 2",
            repetitions=0,
        )
        await card_repo.create(
            deck_id=deck2.id,
            front="Word 3",
            back="Translation 3",
            repetitions=0,
        )

        count = await card_repo.count_new_cards_from_decks([deck1.id, deck2.id])
        assert count == 3

    async def test_count_due_cards_from_multiple_decks(
        self, db_session: AsyncSession, deck1: Deck, deck2: Deck
    ):
        """Test counting due cards from multiple decks."""
        card_repo = CardRepository(db_session)
        past_time = datetime.now(UTC) - timedelta(days=1)

        # Create due cards in both decks
        await card_repo.create(
            deck_id=deck1.id,
            front="Word 1",
            back="Translation 1",
            repetitions=1,
            next_review=past_time,
        )
        await card_repo.create(
            deck_id=deck2.id,
            front="Word 2",
            back="Translation 2",
            repetitions=1,
            next_review=past_time,
        )

        count = await card_repo.count_due_cards_from_decks([deck1.id, deck2.id])
        assert count == 2

    async def test_get_new_cards_with_limit(
        self, db_session: AsyncSession, deck1: Deck, deck2: Deck
    ):
        """Test that limit parameter works for new cards."""
        card_repo = CardRepository(db_session)

        # Create multiple new cards
        for i in range(5):
            await card_repo.create(
                deck_id=deck1.id,
                front=f"Word {i}",
                back=f"Translation {i}",
                repetitions=0,
            )

        new_cards = await card_repo.get_new_cards_from_decks([deck1.id, deck2.id], limit=3)
        assert len(new_cards) == 3

    async def test_get_due_cards_with_limit(
        self, db_session: AsyncSession, deck1: Deck, deck2: Deck
    ):
        """Test that limit parameter works for due cards."""
        card_repo = CardRepository(db_session)
        past_time = datetime.now(UTC) - timedelta(days=1)

        # Create multiple due cards
        for i in range(5):
            await card_repo.create(
                deck_id=deck1.id,
                front=f"Word {i}",
                back=f"Translation {i}",
                repetitions=1,
                next_review=past_time,
            )

        due_cards = await card_repo.get_due_cards_from_decks([deck1.id, deck2.id], limit=3)
        assert len(due_cards) == 3
