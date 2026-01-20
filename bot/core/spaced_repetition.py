"""Spaced Repetition System implementation using SM-2 algorithm.

The SM-2 algorithm (SuperMemo 2) is a well-established spaced repetition algorithm
that calculates optimal review intervals based on user performance.

Reference: https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
"""

from datetime import UTC, datetime, timedelta
from typing import NamedTuple

from bot.core.constants import (
    DEFAULT_EASE_FACTOR,
    EASE_BONUS,
    EASE_FACTOR_MODIFIER,
    HARD_INTERVAL_MULTIPLIER,
    INITIAL_INTERVAL_AGAIN,
    INITIAL_INTERVAL_EASY,
    INITIAL_INTERVAL_GOOD,
    INITIAL_INTERVAL_HARD,
    MAX_INTERVAL_DAYS,
    MIN_EASE_FACTOR,
    QUALITY_AGAIN,
    QUALITY_EASY,
    QUALITY_GOOD,
    QUALITY_HARD,
)


class SRSResult(NamedTuple):
    """Result of spaced repetition calculation."""

    ease_factor: float
    interval: int  # Days
    repetitions: int
    next_review: datetime


def calculate_next_review(
    quality: int,
    ease_factor: float,
    interval: int,
    repetitions: int,
    current_time: datetime | None = None,
) -> SRSResult:
    """Calculate next review parameters using SM-2 algorithm.

    Args:
        quality: Quality of recall (0=Again, 2=Hard, 3=Good, 5=Easy)
        ease_factor: Current ease factor (difficulty multiplier)
        interval: Current interval in days
        repetitions: Number of consecutive successful repetitions
        current_time: Current time (defaults to now)

    Returns:
        SRSResult with updated parameters

    Quality ratings:
        0 (Again): Completely forgot - reset the card
        2 (Hard): Difficult to remember - smaller interval increase
        3 (Good): Correct with effort - normal interval increase
        5 (Easy): Perfect recall - larger interval increase
    """
    if current_time is None:
        current_time = datetime.now(UTC)

    # Validate quality
    if quality not in (QUALITY_AGAIN, QUALITY_HARD, QUALITY_GOOD, QUALITY_EASY):
        raise ValueError(f"Invalid quality rating: {quality}")

    # Calculate new ease factor (only for quality >= 3)
    new_ease_factor = ease_factor
    if quality >= QUALITY_GOOD:
        # SM-2 formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        # Simplified version:
        new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease_factor = max(new_ease_factor, MIN_EASE_FACTOR)

    # Calculate new interval and repetitions
    new_interval: int
    new_repetitions: int

    if quality == QUALITY_AGAIN:
        # Reset card to beginning
        new_interval = INITIAL_INTERVAL_AGAIN
        new_repetitions = 0
        # Reduce ease factor for failed cards
        new_ease_factor = max(ease_factor - EASE_FACTOR_MODIFIER, MIN_EASE_FACTOR)

    elif quality == QUALITY_HARD:
        if repetitions == 0:
            # First time seeing the card
            new_interval = INITIAL_INTERVAL_HARD
            new_repetitions = 1
        else:
            # Increase interval but less than normal
            new_interval = int(interval * HARD_INTERVAL_MULTIPLIER)
            new_repetitions = repetitions + 1
        # Slightly reduce ease factor
        new_ease_factor = max(ease_factor - EASE_FACTOR_MODIFIER * 0.5, MIN_EASE_FACTOR)

    elif quality == QUALITY_GOOD:
        if repetitions == 0:
            # First review - use initial interval
            new_interval = INITIAL_INTERVAL_GOOD
            new_repetitions = 1
        elif repetitions == 1:
            # Second review
            new_interval = 6
            new_repetitions = 2
        else:
            # Subsequent reviews - use ease factor
            new_interval = int(interval * new_ease_factor)
            new_repetitions = repetitions + 1

    else:  # QUALITY_EASY
        if repetitions == 0:
            # First time - use longer initial interval
            new_interval = INITIAL_INTERVAL_EASY
            new_repetitions = 1
        else:
            # Apply bonus for easy recall
            new_interval = int(interval * new_ease_factor * EASE_BONUS)
            new_repetitions = repetitions + 1
        # Increase ease factor slightly
        new_ease_factor = ease_factor + EASE_FACTOR_MODIFIER

    # Cap the interval at maximum
    new_interval = min(new_interval, MAX_INTERVAL_DAYS)

    # Calculate next review datetime
    next_review = current_time + timedelta(days=new_interval)

    return SRSResult(
        ease_factor=new_ease_factor,
        interval=new_interval,
        repetitions=new_repetitions,
        next_review=next_review,
    )


def get_initial_srs_values() -> dict:
    """Get initial SRS values for a new card.

    Returns:
        Dictionary with initial ease_factor, interval, repetitions, next_review
    """
    return {
        "ease_factor": DEFAULT_EASE_FACTOR,
        "interval": 0,
        "repetitions": 0,
        "next_review": datetime.now(UTC),
    }


def is_card_in_learning(repetitions: int) -> bool:
    """Check if card is still in learning phase.

    Args:
        repetitions: Number of successful repetitions

    Returns:
        True if card is in learning phase
    """
    return repetitions < 2


def get_quality_label(quality: int) -> str:
    """Get human-readable label for quality rating.

    Args:
        quality: Quality rating

    Returns:
        Label string
    """
    labels = {
        QUALITY_AGAIN: "Again",
        QUALITY_HARD: "Hard",
        QUALITY_GOOD: "Good",
        QUALITY_EASY: "Easy",
    }
    return labels.get(quality, "Unknown")
