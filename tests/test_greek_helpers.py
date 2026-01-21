"""Tests for Greek helper utilities."""

import pytest

from bot.utils.greek_helpers import (
    get_article_gender,
    get_gender_label_russian,
    has_greek_article,
)


class TestHasGreekArticle:
    """Tests for has_greek_article function."""

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("ο σκύλος", True),
            ("η γάτα", True),
            ("το σπίτι", True),
            ("οι άνθρωποι", True),
            ("τα παιδιά", True),
            ("σκύλος", False),
            ("γάτα", False),
            ("καλημέρα", False),
            ("", False),
            ("   ", False),
        ],
    )
    def test_has_greek_article(self, text: str, expected: bool):
        """Test article detection."""
        assert has_greek_article(text) == expected

    def test_case_insensitive(self):
        """Test that article detection is case insensitive."""
        assert has_greek_article("Ο σκύλος") is True
        assert has_greek_article("Η γάτα") is True
        assert has_greek_article("Το σπίτι") is True


class TestGetArticleGender:
    """Tests for get_article_gender function."""

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("ο σκύλος", "masculine"),
            ("η γάτα", "feminine"),
            ("το σπίτι", "neuter"),
            ("οι άνθρωποι", "masculine_plural"),
            ("τα παιδιά", "neuter_plural"),
            ("σκύλος", None),
            ("", None),
        ],
    )
    def test_get_article_gender(self, text: str, expected: str | None):
        """Test gender extraction from article."""
        assert get_article_gender(text) == expected


class TestGetGenderLabelRussian:
    """Tests for get_gender_label_russian function."""

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("ο σκύλος", " (м.р.)"),
            ("η γάτα", " (ж.р.)"),
            ("το σπίτι", " (ср.р.)"),
            ("οι άνθρωποι", " (мн.ч.)"),
            ("τα παιδιά", " (мн.ч.)"),
            ("σκύλος", ""),
            ("hello", ""),
            ("", ""),
        ],
    )
    def test_get_gender_label_russian(self, text: str, expected: str):
        """Test Russian gender label generation."""
        assert get_gender_label_russian(text) == expected
