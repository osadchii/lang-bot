"""Card scheduling and prioritization logic."""

from datetime import UTC, datetime
from typing import NamedTuple

from bot.database.models.card import Card


class ScheduledCard(NamedTuple):
    """Card with scheduling priority."""

    card: Card
    priority: int  # Lower number = higher priority


def prioritize_cards(cards: list[Card], current_time: datetime | None = None) -> list[Card]:
    """Prioritize cards for review based on various factors.

    Priority order:
    1. Overdue cards (oldest first)
    2. New cards (by creation date)
    3. Due cards (by due date)

    Args:
        cards: List of cards to prioritize
        current_time: Current time (defaults to now)

    Returns:
        Sorted list of cards by priority
    """
    if current_time is None:
        current_time = datetime.now(UTC)

    scheduled_cards: list[ScheduledCard] = []

    for card in cards:
        priority = _calculate_priority(card, current_time)
        scheduled_cards.append(ScheduledCard(card=card, priority=priority))

    # Sort by priority (lower = higher priority)
    scheduled_cards.sort(key=lambda x: x.priority)

    return [sc.card for sc in scheduled_cards]


def _calculate_priority(card: Card, current_time: datetime) -> int:
    """Calculate priority score for a card.

    Lower score = higher priority.

    Args:
        card: Card to calculate priority for
        current_time: Current time

    Returns:
        Priority score
    """
    # New cards (never reviewed) get high priority
    if card.repetitions == 0:
        # Use negative timestamp to prioritize older new cards first
        return int(-card.created_at.timestamp())

    # Calculate how overdue the card is
    time_diff = (current_time - card.next_review).total_seconds()

    # Overdue cards get highest priority (negative value)
    if time_diff > 0:
        # More overdue = higher priority (more negative)
        return -int(time_diff)

    # Not yet due - lower priority (positive value)
    return int(-time_diff)


def mix_new_and_review_cards(
    new_cards: list[Card],
    review_cards: list[Card],
    new_cards_limit: int = 5,
    total_limit: int = 20,
) -> list[Card]:
    """Mix new cards and review cards in a balanced way.

    Args:
        new_cards: List of new cards
        review_cards: List of cards due for review
        new_cards_limit: Maximum number of new cards to include
        total_limit: Total maximum number of cards

    Returns:
        Mixed list of cards
    """
    # Limit new cards
    selected_new = new_cards[:new_cards_limit]

    # Calculate remaining slots for review cards
    remaining_slots = total_limit - len(selected_new)
    selected_review = review_cards[:remaining_slots]

    # Interleave new and review cards
    result: list[Card] = []
    new_idx = 0
    review_idx = 0

    # Mix ratio: 1 new card for every 3 review cards
    while new_idx < len(selected_new) or review_idx < len(selected_review):
        # Add review cards
        for _ in range(3):
            if review_idx < len(selected_review):
                result.append(selected_review[review_idx])
                review_idx += 1

        # Add one new card
        if new_idx < len(selected_new):
            result.append(selected_new[new_idx])
            new_idx += 1

    return result[:total_limit]


def get_next_card_for_learning(
    deck_cards: list[Card], current_time: datetime | None = None
) -> Card | None:
    """Get the next card to show in a learning session.

    Args:
        deck_cards: All cards in the deck
        current_time: Current time (defaults to now)

    Returns:
        Next card to review or None if no cards available
    """
    if not deck_cards:
        return None

    if current_time is None:
        current_time = datetime.now(UTC)

    # Separate new and due cards
    new_cards = [c for c in deck_cards if c.repetitions == 0]
    due_cards = [c for c in deck_cards if c.repetitions > 0 and c.is_due]

    # Prioritize due cards, then new cards
    prioritized = prioritize_cards(due_cards + new_cards, current_time)

    return prioritized[0] if prioritized else None
