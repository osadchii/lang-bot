"""Card repository."""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.card import Card
from bot.database.repositories.base import BaseRepository


class CardRepository(BaseRepository[Card]):
    """Repository for Card model."""

    def __init__(self, session: AsyncSession):
        """Initialize card repository.

        Args:
            session: Async database session
        """
        super().__init__(Card, session)

    async def get_deck_cards(
        self, deck_id: int, limit: int | None = None, offset: int = 0
    ) -> list[Card]:
        """Get all cards in a deck.

        Args:
            deck_id: Deck ID
            limit: Maximum number of cards to return
            offset: Number of cards to skip

        Returns:
            List of card instances
        """
        query = select(Card).where(Card.deck_id == deck_id).offset(offset)

        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_due_cards(
        self,
        deck_id: int,
        limit: int | None = None,
        current_time: datetime | None = None,
    ) -> list[Card]:
        """Get cards that are due for review.

        Args:
            deck_id: Deck ID
            limit: Maximum number of cards to return
            current_time: Current time (defaults to now)

        Returns:
            List of due cards, ordered by next_review (oldest first)
        """
        if current_time is None:
            current_time = datetime.now(UTC)

        query = (
            select(Card)
            .where(
                Card.deck_id == deck_id,
                Card.next_review <= current_time,
                Card.repetitions > 0,  # Exclude new cards (they're handled separately)
            )
            .order_by(Card.next_review.asc())
        )

        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_new_cards(self, deck_id: int, limit: int | None = None) -> list[Card]:
        """Get new cards (never reviewed).

        Args:
            deck_id: Deck ID
            limit: Maximum number of cards to return

        Returns:
            List of new cards
        """
        query = select(Card).where(Card.deck_id == deck_id, Card.repetitions == 0)

        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_due_cards(self, deck_id: int, current_time: datetime | None = None) -> int:
        """Count cards due for review.

        Args:
            deck_id: Deck ID
            current_time: Current time (defaults to now)

        Returns:
            Number of due cards
        """
        if current_time is None:
            current_time = datetime.now(UTC)

        query = (
            select(func.count())
            .select_from(Card)
            .where(
                Card.deck_id == deck_id,
                Card.next_review <= current_time,
                Card.repetitions > 0,  # Exclude new cards (they're handled separately)
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def count_new_cards(self, deck_id: int) -> int:
        """Count new cards (never reviewed).

        Args:
            deck_id: Deck ID

        Returns:
            Number of new cards
        """
        query = (
            select(func.count())
            .select_from(Card)
            .where(Card.deck_id == deck_id, Card.repetitions == 0)
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def search_cards(self, deck_id: int, search_term: str) -> list[Card]:
        """Search cards by front or back text.

        Args:
            deck_id: Deck ID
            search_term: Search term

        Returns:
            List of matching cards
        """
        search_pattern = f"%{search_term}%"
        query = select(Card).where(
            Card.deck_id == deck_id,
            (Card.front.ilike(search_pattern)) | (Card.back.ilike(search_pattern)),
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search_user_cards(
        self,
        user_id: int,
        search_term: str,
        limit: int = 10,
    ) -> list[tuple[Card, int]]:
        """Search all user's cards across all decks.

        Args:
            user_id: User ID
            search_term: Search term
            limit: Maximum results

        Returns:
            List of (Card, deck_id) tuples for matching cards
        """
        from bot.database.models.deck import Deck

        search_pattern = f"%{search_term}%"
        query = (
            select(Card, Deck.id)
            .join(Deck, Card.deck_id == Deck.id)
            .where(
                Deck.user_id == user_id,
                (Card.front.ilike(search_pattern)) | (Card.back.ilike(search_pattern)),
            )
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.tuples().all())

    async def get_due_cards_from_decks(
        self,
        deck_ids: list[int],
        limit: int | None = None,
        current_time: datetime | None = None,
    ) -> list[Card]:
        """Get cards due for review from multiple decks.

        Args:
            deck_ids: List of deck IDs
            limit: Maximum number of cards to return
            current_time: Current time (defaults to now)

        Returns:
            List of due cards, ordered by next_review (oldest first)
        """
        if not deck_ids:
            return []

        if current_time is None:
            current_time = datetime.now(UTC)

        query = (
            select(Card)
            .where(
                Card.deck_id.in_(deck_ids),
                Card.next_review <= current_time,
                Card.repetitions > 0,
            )
            .order_by(Card.next_review.asc())
        )

        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_new_cards_from_decks(
        self,
        deck_ids: list[int],
        limit: int | None = None,
    ) -> list[Card]:
        """Get new cards (never reviewed) from multiple decks.

        Args:
            deck_ids: List of deck IDs
            limit: Maximum number of cards to return

        Returns:
            List of new cards
        """
        if not deck_ids:
            return []

        query = (
            select(Card)
            .where(
                Card.deck_id.in_(deck_ids),
                Card.repetitions == 0,
            )
            .order_by(Card.created_at.asc())
        )

        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_due_cards_from_decks(
        self,
        deck_ids: list[int],
        current_time: datetime | None = None,
    ) -> int:
        """Count cards due for review from multiple decks.

        Args:
            deck_ids: List of deck IDs
            current_time: Current time (defaults to now)

        Returns:
            Number of due cards
        """
        if not deck_ids:
            return 0

        if current_time is None:
            current_time = datetime.now(UTC)

        query = (
            select(func.count())
            .select_from(Card)
            .where(
                Card.deck_id.in_(deck_ids),
                Card.next_review <= current_time,
                Card.repetitions > 0,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def count_new_cards_from_decks(self, deck_ids: list[int]) -> int:
        """Count new cards from multiple decks.

        Args:
            deck_ids: List of deck IDs

        Returns:
            Number of new cards
        """
        if not deck_ids:
            return 0

        query = (
            select(func.count())
            .select_from(Card)
            .where(
                Card.deck_id.in_(deck_ids),
                Card.repetitions == 0,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def find_cards_by_lemmas(
        self,
        user_id: int,
        lemmas: list[str],
        limit: int = 100,
    ) -> list[tuple[Card, int]]:
        """Find cards matching any of the provided lemmas.

        Searches both front and back fields. Useful for bulk vocabulary check.

        Args:
            user_id: User ID
            lemmas: List of lemmas to search for
            limit: Maximum results

        Returns:
            List of (Card, deck_id) tuples for matching cards
        """
        from sqlalchemy import or_

        from bot.database.models.deck import Deck

        if not lemmas:
            return []

        # Build OR conditions for all lemmas (exact match, case-insensitive)
        conditions = []
        for lemma in lemmas:
            lemma_lower = lemma.lower()
            conditions.append(func.lower(Card.front) == lemma_lower)
            conditions.append(func.lower(Card.back) == lemma_lower)

        query = (
            select(Card, Deck.id)
            .join(Deck, Card.deck_id == Deck.id)
            .where(
                Deck.user_id == user_id,
                or_(*conditions),
            )
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.tuples().all())
