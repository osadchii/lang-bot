"""Tests for spaced repetition system."""

from datetime import UTC, datetime, timedelta

import pytest

from bot.core.constants import (
    DEFAULT_EASE_FACTOR,
    INITIAL_INTERVAL_AGAIN,
    INITIAL_INTERVAL_EASY,
    INITIAL_INTERVAL_REMEMBERED,
    MIN_EASE_FACTOR,
    QUALITY_EASY,
    QUALITY_FORGOT,
    QUALITY_REMEMBERED,
)
from bot.core.spaced_repetition import (
    calculate_next_review,
    get_initial_srs_values,
    get_quality_label,
    is_card_in_learning,
)


class TestCalculateNextReview:
    """Tests for calculate_next_review function."""

    def test_forgot_resets_card(self):
        """Test that FORGOT response resets card to beginning."""
        result = calculate_next_review(
            quality=QUALITY_FORGOT,
            ease_factor=2.5,
            interval=10,
            repetitions=5,
        )

        assert result.interval == INITIAL_INTERVAL_AGAIN
        assert result.repetitions == 0
        assert result.ease_factor < 2.5  # Reduced

    def test_remembered_first_review(self):
        """Test REMEMBERED response on first review."""
        result = calculate_next_review(
            quality=QUALITY_REMEMBERED,
            ease_factor=DEFAULT_EASE_FACTOR,
            interval=0,
            repetitions=0,
        )

        assert result.interval == INITIAL_INTERVAL_REMEMBERED
        assert result.repetitions == 1

    def test_remembered_second_review(self):
        """Test REMEMBERED response on second review."""
        result = calculate_next_review(
            quality=QUALITY_REMEMBERED,
            ease_factor=DEFAULT_EASE_FACTOR,
            interval=1,
            repetitions=1,
        )

        assert result.interval == 6
        assert result.repetitions == 2

    def test_remembered_subsequent_review(self):
        """Test REMEMBERED response on subsequent reviews uses ease factor."""
        result = calculate_next_review(
            quality=QUALITY_REMEMBERED,
            ease_factor=2.5,
            interval=6,
            repetitions=2,
        )

        assert result.interval > 6  # Should increase
        assert result.repetitions == 3

    def test_easy_first_review(self):
        """Test EASY response on first review."""
        result = calculate_next_review(
            quality=QUALITY_EASY,
            ease_factor=DEFAULT_EASE_FACTOR,
            interval=0,
            repetitions=0,
        )

        assert result.interval == INITIAL_INTERVAL_EASY
        assert result.repetitions == 1

    def test_easy_subsequent_review(self):
        """Test EASY response on subsequent reviews applies bonus."""
        result = calculate_next_review(
            quality=QUALITY_EASY,
            ease_factor=2.5,
            interval=6,
            repetitions=2,
        )

        # Easy should result in longer interval than remembered
        remembered_result = calculate_next_review(
            quality=QUALITY_REMEMBERED,
            ease_factor=2.5,
            interval=6,
            repetitions=2,
        )

        assert result.interval > remembered_result.interval

    def test_invalid_quality_raises_error(self):
        """Test that invalid quality value raises ValueError."""
        with pytest.raises(ValueError, match="Invalid quality rating"):
            calculate_next_review(
                quality=2,  # Invalid - not in [0, 3, 5]
                ease_factor=2.5,
                interval=0,
                repetitions=0,
            )

    def test_ease_factor_not_below_minimum(self):
        """Test that ease factor never goes below minimum."""
        result = calculate_next_review(
            quality=QUALITY_FORGOT,
            ease_factor=MIN_EASE_FACTOR,
            interval=1,
            repetitions=1,
        )

        assert result.ease_factor >= MIN_EASE_FACTOR

    def test_next_review_datetime(self):
        """Test that next_review datetime is calculated correctly."""
        current = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        result = calculate_next_review(
            quality=QUALITY_REMEMBERED,
            ease_factor=2.5,
            interval=0,
            repetitions=0,
            current_time=current,
        )

        expected = current + timedelta(days=INITIAL_INTERVAL_REMEMBERED)
        assert result.next_review == expected


class TestGetInitialSrsValues:
    """Tests for get_initial_srs_values function."""

    def test_returns_default_values(self):
        """Test that initial values are correct."""
        values = get_initial_srs_values()

        assert values["ease_factor"] == DEFAULT_EASE_FACTOR
        assert values["interval"] == 0
        assert values["repetitions"] == 0
        assert "next_review" in values


class TestIsCardInLearning:
    """Tests for is_card_in_learning function."""

    def test_zero_repetitions_in_learning(self):
        """Test that card with 0 repetitions is in learning."""
        assert is_card_in_learning(0) is True

    def test_one_repetition_in_learning(self):
        """Test that card with 1 repetition is still in learning."""
        assert is_card_in_learning(1) is True

    def test_two_repetitions_not_in_learning(self):
        """Test that card with 2+ repetitions is not in learning."""
        assert is_card_in_learning(2) is False
        assert is_card_in_learning(5) is False


class TestGetQualityLabel:
    """Tests for get_quality_label function."""

    def test_forgot_label(self):
        """Test label for FORGOT quality."""
        assert get_quality_label(QUALITY_FORGOT) == "Forgot"

    def test_remembered_label(self):
        """Test label for REMEMBERED quality."""
        assert get_quality_label(QUALITY_REMEMBERED) == "Remembered"

    def test_easy_label(self):
        """Test label for EASY quality."""
        assert get_quality_label(QUALITY_EASY) == "Easy"

    def test_unknown_quality(self):
        """Test label for unknown quality value."""
        assert get_quality_label(99) == "Unknown"
