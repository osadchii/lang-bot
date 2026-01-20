"""Learning service for managing study sessions and card reviews."""

import asyncio
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from bot.config.logging_config import get_logger
from bot.core.card_scheduler import (
    get_next_card_for_learning,
    mix_new_and_review_cards,
    prioritize_cards,
)
from bot.core.constants import (
    DEFAULT_CARDS_PER_SESSION,
    MAX_INTERVAL_DAYS,
    MAX_NEW_CARDS_PER_DAY,
    MIN_EASE_FACTOR,
)
from bot.core.spaced_repetition import SRSResult, calculate_next_review
from bot.database.models.card import Card
from bot.database.repositories.card_repo import CardRepository
from bot.database.repositories.review_repo import ReviewRepository

logger = get_logger(__name__)


def validate_srs_result(result: SRSResult) -> bool:
    """Validate SRS calculation results.

    Args:
        result: SRS calculation result to validate

    Returns:
        True if valid, False otherwise
    """
    if result.ease_factor < MIN_EASE_FACTOR or result.ease_factor > 3.0:
        logger.error(f"Invalid ease_factor: {result.ease_factor}")
        return False
    if result.interval < 0 or result.interval > MAX_INTERVAL_DAYS:
        logger.error(f"Invalid interval: {result.interval}")
        return False
    if result.repetitions < 0:
        logger.error(f"Invalid repetitions: {result.repetitions}")
        return False
    return True


class LearningService:
    """Service for learning session management."""

    def __init__(self, session: AsyncSession):
        """Initialize learning service.

        Args:
            session: Async database session
        """
        self.card_repo = CardRepository(session)
        self.review_repo = ReviewRepository(session)
        self.session = session

    async def get_learning_session(
        self,
        deck_id: int,
        max_cards: int = DEFAULT_CARDS_PER_SESSION,
        max_new_cards: int = MAX_NEW_CARDS_PER_DAY,
    ) -> list[Card]:
        """Get cards for a learning session.

        Args:
            deck_id: Deck ID
            max_cards: Maximum total cards
            max_new_cards: Maximum new cards to include

        Returns:
            List of cards for the session
        """
        # Get new and due cards
        new_cards = await self.card_repo.get_new_cards(deck_id, limit=max_new_cards)
        due_cards = await self.card_repo.get_due_cards(deck_id, limit=max_cards)

        # Prioritize due cards
        due_cards = prioritize_cards(due_cards)

        # Mix new and review cards
        session_cards = mix_new_and_review_cards(
            new_cards=new_cards,
            review_cards=due_cards,
            new_cards_limit=max_new_cards,
            total_limit=max_cards,
        )

        return session_cards

    async def get_next_card(self, deck_id: int) -> Card | None:
        """Get the next card to review.

        Args:
            deck_id: Deck ID

        Returns:
            Next card or None if no cards available
        """
        # Get all cards in deck
        all_cards = await self.card_repo.get_deck_cards(deck_id)

        return get_next_card_for_learning(all_cards)

    async def process_card_review(
        self,
        card_id: int,
        user_id: int,
        quality: int,
        time_spent: int | None = None,
        current_time: datetime | None = None,
    ) -> Card:
        """Process a card review and update SRS data.

        Args:
            card_id: Card ID
            user_id: User ID
            quality: Quality rating (0, 2, 3, 5)
            time_spent: Time spent on card in seconds
            current_time: Current time (defaults to now)

        Returns:
            Updated card instance
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        # Get card
        card = await self.card_repo.get_by_id(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")

        # Store state before review (for analytics)
        ease_factor_before = card.ease_factor
        interval_before = card.interval

        # Calculate new SRS values
        srs_result = calculate_next_review(
            quality=quality,
            ease_factor=card.ease_factor,
            interval=card.interval,
            repetitions=card.repetitions,
            current_time=current_time,
        )

        # Validate before applying
        if not validate_srs_result(srs_result):
            raise ValueError("Invalid SRS calculation result")

        # Update card with new SRS values
        card.ease_factor = srs_result.ease_factor
        card.interval = srs_result.interval
        card.repetitions = srs_result.repetitions
        card.next_review = srs_result.next_review

        # Update statistics
        card.total_reviews += 1
        if quality >= 3:  # Good or Easy
            card.correct_reviews += 1

        await self.session.flush()
        await self.session.refresh(card)

        # Create review record
        await self.review_repo.create(
            card_id=card_id,
            user_id=user_id,
            quality=quality,
            reviewed_at=current_time,
            time_spent=time_spent,
            ease_factor_before=ease_factor_before,
            interval_before=interval_before,
        )

        return card

    async def get_deck_stats(self, deck_id: int) -> dict:
        """Get statistics for a deck.

        Args:
            deck_id: Deck ID

        Returns:
            Dictionary with deck statistics
        """
        # Parallelize independent queries
        all_cards, new_cards, due_cards = await asyncio.gather(
            self.card_repo.get_deck_cards(deck_id),
            self.card_repo.count_new_cards(deck_id),
            self.card_repo.count_due_cards(deck_id),
        )

        total_cards = len(all_cards)

        return {
            "total_cards": total_cards,
            "new_cards": new_cards,
            "due_cards": due_cards,
            "learning_cards": total_cards - new_cards,
        }
