"""Deck service for managing card decks."""

from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.deck import Deck
from bot.database.repositories.deck_repo import DeckRepository


class DeckService:
    """Service for deck operations."""

    def __init__(self, session: AsyncSession):
        """Initialize deck service.

        Args:
            session: Async database session
        """
        self.repo = DeckRepository(session)

    async def create_deck(self, user_id: int, name: str, description: str | None = None) -> Deck:
        """Create a new deck.

        Args:
            user_id: User ID
            name: Deck name
            description: Deck description

        Returns:
            Created deck instance
        """
        return await self.repo.create(user_id=user_id, name=name, description=description)

    async def get_deck(self, deck_id: int) -> Deck | None:
        """Get deck by ID.

        Args:
            deck_id: Deck ID

        Returns:
            Deck instance or None
        """
        return await self.repo.get_by_id(deck_id)

    async def get_user_decks(
        self, user_id: int, limit: int | None = None, offset: int = 0
    ) -> list[Deck]:
        """Get all decks for a user.

        Args:
            user_id: User ID
            limit: Maximum number of decks
            offset: Number of decks to skip

        Returns:
            List of deck instances
        """
        return await self.repo.get_user_decks(user_id, limit, offset)

    async def get_deck_by_name(self, user_id: int, name: str) -> Deck | None:
        """Get deck by name for a user.

        Args:
            user_id: User ID
            name: Deck name

        Returns:
            Deck instance or None
        """
        return await self.repo.get_deck_by_name(user_id, name)

    async def get_deck_with_stats(self, deck_id: int) -> tuple[Deck | None, int]:
        """Get deck with card count.

        Args:
            deck_id: Deck ID

        Returns:
            Tuple of (Deck instance or None, card count)
        """
        return await self.repo.get_deck_with_card_count(deck_id)

    async def update_deck(
        self, deck: Deck, name: str | None = None, description: str | None = None
    ) -> Deck:
        """Update deck information.

        Args:
            deck: Deck instance to update
            name: New deck name
            description: New deck description

        Returns:
            Updated deck instance
        """
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description

        if update_data:
            return await self.repo.update(deck, **update_data)
        return deck

    async def delete_deck(self, deck: Deck) -> None:
        """Delete a deck and all its cards.

        Args:
            deck: Deck instance to delete
        """
        await self.repo.delete(deck)

    async def count_user_decks(self, user_id: int) -> int:
        """Count total decks for a user.

        Args:
            user_id: User ID

        Returns:
            Total deck count
        """
        return await self.repo.count_user_decks(user_id)

    async def get_user_decks_sorted(self, user_id: int) -> list[Deck]:
        """Get all decks for a user, sorted (active first, then by name).

        Args:
            user_id: User ID

        Returns:
            List of deck instances, active first
        """
        return await self.repo.get_user_decks_sorted(user_id)

    async def get_active_decks(self, user_id: int) -> list[Deck]:
        """Get active decks for a user.

        Args:
            user_id: User ID

        Returns:
            List of active deck instances
        """
        return await self.repo.get_user_active_decks(user_id)

    async def has_active_decks(self, user_id: int) -> bool:
        """Check if user has any active decks.

        Args:
            user_id: User ID

        Returns:
            True if user has at least one active deck
        """
        count = await self.repo.count_active_decks(user_id)
        return count > 0

    async def toggle_deck_active(self, deck: Deck) -> Deck:
        """Toggle deck active status.

        Args:
            deck: Deck instance to toggle

        Returns:
            Updated deck instance
        """
        return await self.repo.update(deck, is_active=not deck.is_active)
