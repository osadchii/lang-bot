"""Deck repository."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.card import Card
from bot.database.models.deck import Deck
from bot.database.repositories.base import BaseRepository


class DeckRepository(BaseRepository[Deck]):
    """Repository for Deck model."""

    def __init__(self, session: AsyncSession):
        """Initialize deck repository.

        Args:
            session: Async database session
        """
        super().__init__(Deck, session)

    async def get_user_decks(
        self, user_id: int, limit: int | None = None, offset: int = 0
    ) -> list[Deck]:
        """Get all decks for a user.

        Args:
            user_id: User ID
            limit: Maximum number of decks to return
            offset: Number of decks to skip

        Returns:
            List of deck instances
        """
        query = select(Deck).where(Deck.user_id == user_id).offset(offset)

        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_deck_by_name(self, user_id: int, name: str) -> Deck | None:
        """Get deck by name for a specific user.

        Args:
            user_id: User ID
            name: Deck name

        Returns:
            Deck instance or None if not found
        """
        query = select(Deck).where(Deck.user_id == user_id, Deck.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_deck_with_card_count(self, deck_id: int) -> tuple[Deck | None, int]:
        """Get deck with total card count.

        Args:
            deck_id: Deck ID

        Returns:
            Tuple of (Deck instance or None, card count)
        """
        deck = await self.get_by_id(deck_id)
        if not deck:
            return None, 0

        # Count cards in this deck
        query = select(func.count()).select_from(Card).where(Card.deck_id == deck_id)
        result = await self.session.execute(query)
        card_count = result.scalar_one()

        return deck, card_count

    async def count_user_decks(self, user_id: int) -> int:
        """Count total number of decks for a user.

        Args:
            user_id: User ID

        Returns:
            Total deck count
        """
        query = select(func.count()).select_from(Deck).where(Deck.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_user_decks_sorted(self, user_id: int) -> list[Deck]:
        """Get all decks for a user, sorted by is_active (active first), then by name.

        Args:
            user_id: User ID

        Returns:
            List of deck instances, active first
        """
        query = (
            select(Deck).where(Deck.user_id == user_id).order_by(Deck.is_active.desc(), Deck.name)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_user_active_decks(self, user_id: int) -> list[Deck]:
        """Get all active decks for a user.

        Args:
            user_id: User ID

        Returns:
            List of active deck instances
        """
        query = select(Deck).where(Deck.user_id == user_id, Deck.is_active == True)  # noqa: E712
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_active_decks(self, user_id: int) -> int:
        """Count active decks for a user.

        Args:
            user_id: User ID

        Returns:
            Number of active decks
        """
        query = (
            select(func.count())
            .select_from(Deck)
            .where(Deck.user_id == user_id, Deck.is_active == True)  # noqa: E712
        )
        result = await self.session.execute(query)
        return result.scalar_one()
