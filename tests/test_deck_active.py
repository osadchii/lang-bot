"""Tests for deck is_active functionality."""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.deck import Deck
from bot.database.models.user import User
from bot.database.repositories.deck_repo import DeckRepository
from bot.database.repositories.user_repo import UserRepository


@pytest_asyncio.fixture
async def user(db_session: AsyncSession, sample_user_data: dict) -> User:
    """Create a user for testing."""
    user_repo = UserRepository(db_session)
    return await user_repo.create(**sample_user_data)


@pytest_asyncio.fixture
async def active_deck(db_session: AsyncSession, user: User) -> Deck:
    """Create an active deck for testing."""
    deck_repo = DeckRepository(db_session)
    return await deck_repo.create(
        user_id=user.id,
        name="Active Deck",
        description="An active test deck",
        is_active=True,
    )


@pytest_asyncio.fixture
async def inactive_deck(db_session: AsyncSession, user: User) -> Deck:
    """Create an inactive deck for testing."""
    deck_repo = DeckRepository(db_session)
    return await deck_repo.create(
        user_id=user.id,
        name="Inactive Deck",
        description="An inactive test deck",
        is_active=False,
    )


class TestDeckIsActiveField:
    """Tests for Deck.is_active field."""

    async def test_deck_default_is_active(self, db_session: AsyncSession, user: User):
        """Test that decks are active by default."""
        deck_repo = DeckRepository(db_session)
        deck = await deck_repo.create(
            user_id=user.id,
            name="Default Deck",
            description="A default test deck",
        )
        assert deck.is_active is True

    async def test_deck_can_be_created_inactive(
        self, db_session: AsyncSession, inactive_deck: Deck
    ):
        """Test that decks can be created as inactive."""
        assert inactive_deck.is_active is False


class TestDeckRepositorySortedMethods:
    """Tests for DeckRepository sorted methods."""

    async def test_get_user_decks_sorted_active_first(
        self,
        db_session: AsyncSession,
        user: User,
        active_deck: Deck,
        inactive_deck: Deck,
    ):
        """Test that active decks appear before inactive decks."""
        deck_repo = DeckRepository(db_session)
        decks = await deck_repo.get_user_decks_sorted(user.id)

        assert len(decks) == 2
        # Active deck should be first
        assert decks[0].is_active is True
        assert decks[1].is_active is False

    async def test_get_user_decks_sorted_by_name_within_status(
        self, db_session: AsyncSession, user: User
    ):
        """Test that decks are sorted by name within active/inactive groups."""
        deck_repo = DeckRepository(db_session)

        # Create decks with specific names
        await deck_repo.create(user_id=user.id, name="Zebra Active", is_active=True)
        await deck_repo.create(user_id=user.id, name="Alpha Active", is_active=True)
        await deck_repo.create(user_id=user.id, name="Zebra Inactive", is_active=False)
        await deck_repo.create(user_id=user.id, name="Alpha Inactive", is_active=False)

        decks = await deck_repo.get_user_decks_sorted(user.id)

        assert len(decks) == 4
        # Active decks first, alphabetically
        assert decks[0].name == "Alpha Active"
        assert decks[1].name == "Zebra Active"
        # Then inactive decks, alphabetically
        assert decks[2].name == "Alpha Inactive"
        assert decks[3].name == "Zebra Inactive"

    async def test_get_user_active_decks(
        self,
        db_session: AsyncSession,
        user: User,
        active_deck: Deck,
        inactive_deck: Deck,
    ):
        """Test getting only active decks."""
        deck_repo = DeckRepository(db_session)
        active_decks = await deck_repo.get_user_active_decks(user.id)

        assert len(active_decks) == 1
        assert active_decks[0].id == active_deck.id
        assert active_decks[0].is_active is True

    async def test_count_active_decks(
        self,
        db_session: AsyncSession,
        user: User,
        active_deck: Deck,
        inactive_deck: Deck,
    ):
        """Test counting active decks."""
        deck_repo = DeckRepository(db_session)
        count = await deck_repo.count_active_decks(user.id)
        assert count == 1

    async def test_count_active_decks_none(self, db_session: AsyncSession, user: User):
        """Test counting active decks when there are none."""
        deck_repo = DeckRepository(db_session)

        # Create only inactive deck
        await deck_repo.create(user_id=user.id, name="Only Inactive", is_active=False)

        count = await deck_repo.count_active_decks(user.id)
        assert count == 0


class TestDeckToggle:
    """Tests for deck toggle functionality."""

    async def test_toggle_active_to_inactive(self, db_session: AsyncSession, active_deck: Deck):
        """Test toggling an active deck to inactive."""
        deck_repo = DeckRepository(db_session)

        assert active_deck.is_active is True
        updated_deck = await deck_repo.update(active_deck, is_active=False)

        assert updated_deck.is_active is False

    async def test_toggle_inactive_to_active(self, db_session: AsyncSession, inactive_deck: Deck):
        """Test toggling an inactive deck to active."""
        deck_repo = DeckRepository(db_session)

        assert inactive_deck.is_active is False
        updated_deck = await deck_repo.update(inactive_deck, is_active=True)

        assert updated_deck.is_active is True
