"""Card service for managing flashcards."""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from bot.core.spaced_repetition import get_initial_srs_values
from bot.database.models.card import Card
from bot.database.repositories.card_repo import CardRepository


class CardService:
    """Service for card operations."""

    def __init__(self, session: AsyncSession):
        """Initialize card service.

        Args:
            session: Async database session
        """
        self.repo = CardRepository(session)

    async def create_card(
        self,
        deck_id: int,
        front: str,
        back: str,
        example: str | None = None,
        notes: str | None = None,
    ) -> Card:
        """Create a new flashcard.

        Args:
            deck_id: Deck ID
            front: Front side (Greek text)
            back: Back side (translation)
            example: Example sentence
            notes: Additional notes

        Returns:
            Created card instance
        """
        # Get initial SRS values
        srs_values = get_initial_srs_values()

        return await self.repo.create(
            deck_id=deck_id,
            front=front,
            back=back,
            example=example,
            notes=notes,
            **srs_values,
        )

    async def get_card(self, card_id: int) -> Card | None:
        """Get card by ID.

        Args:
            card_id: Card ID

        Returns:
            Card instance or None
        """
        return await self.repo.get_by_id(card_id)

    async def get_deck_cards(
        self, deck_id: int, limit: int | None = None, offset: int = 0
    ) -> list[Card]:
        """Get all cards in a deck.

        Args:
            deck_id: Deck ID
            limit: Maximum number of cards
            offset: Number of cards to skip

        Returns:
            List of card instances
        """
        return await self.repo.get_deck_cards(deck_id, limit, offset)

    async def get_due_cards(
        self, deck_id: int, limit: int | None = None, current_time: datetime | None = None
    ) -> list[Card]:
        """Get cards due for review.

        Args:
            deck_id: Deck ID
            limit: Maximum number of cards
            current_time: Current time (defaults to now)

        Returns:
            List of due cards
        """
        return await self.repo.get_due_cards(deck_id, limit, current_time)

    async def get_new_cards(self, deck_id: int, limit: int | None = None) -> list[Card]:
        """Get new cards (never reviewed).

        Args:
            deck_id: Deck ID
            limit: Maximum number of cards

        Returns:
            List of new cards
        """
        return await self.repo.get_new_cards(deck_id, limit)

    async def count_due_cards(self, deck_id: int, current_time: datetime | None = None) -> int:
        """Count cards due for review.

        Args:
            deck_id: Deck ID
            current_time: Current time (defaults to now)

        Returns:
            Number of due cards
        """
        return await self.repo.count_due_cards(deck_id, current_time)

    async def count_new_cards(self, deck_id: int) -> int:
        """Count new cards.

        Args:
            deck_id: Deck ID

        Returns:
            Number of new cards
        """
        return await self.repo.count_new_cards(deck_id)

    async def update_card(
        self,
        card: Card,
        front: str | None = None,
        back: str | None = None,
        example: str | None = None,
        notes: str | None = None,
    ) -> Card:
        """Update card content.

        Args:
            card: Card instance to update
            front: New front text
            back: New back text
            example: New example
            notes: New notes

        Returns:
            Updated card instance
        """
        update_data = {}
        if front is not None:
            update_data["front"] = front
        if back is not None:
            update_data["back"] = back
        if example is not None:
            update_data["example"] = example
        if notes is not None:
            update_data["notes"] = notes

        if update_data:
            return await self.repo.update(card, **update_data)
        return card

    async def delete_card(self, card: Card) -> None:
        """Delete a card.

        Args:
            card: Card instance to delete
        """
        await self.repo.delete(card)

    async def search_cards(self, deck_id: int, search_term: str) -> list[Card]:
        """Search cards by text.

        Args:
            deck_id: Deck ID
            search_term: Search term

        Returns:
            List of matching cards
        """
        return await self.repo.search_cards(deck_id, search_term)
