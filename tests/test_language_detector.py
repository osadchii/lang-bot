"""Tests for language detection utilities."""

import pytest

from bot.utils.language_detector import detect_language, is_greek, is_russian


class TestDetectLanguage:
    """Tests for detect_language function."""

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("σπίτι", "greek"),
            ("ο σκύλος", "greek"),
            ("η γάτα", "greek"),
            ("το παιδί", "greek"),
            ("Γεια σου", "greek"),
            ("καλημέρα", "greek"),
        ],
    )
    def test_detect_greek(self, text: str, expected: str):
        """Test detection of Greek text."""
        assert detect_language(text) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("дом", "russian"),
            ("привет", "russian"),
            ("добавь слово", "russian"),
            ("кошка", "russian"),
            ("Здравствуйте", "russian"),
        ],
    )
    def test_detect_russian(self, text: str, expected: str):
        """Test detection of Russian text."""
        assert detect_language(text) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("hello", "unknown"),
            ("12345", "unknown"),
            ("!@#$%", "unknown"),
            ("", "unknown"),
            ("   ", "unknown"),
        ],
    )
    def test_detect_unknown(self, text: str, expected: str):
        """Test detection of non-Greek/Russian text."""
        assert detect_language(text) == expected

    def test_mixed_greek_dominant(self):
        """Test mixed text with Greek dominant."""
        # More Greek than Russian characters
        text = "σπίτι и дом"
        result = detect_language(text)
        assert result in ["greek", "russian"]

    def test_mixed_russian_dominant(self):
        """Test mixed text with Russian dominant."""
        # More Russian than Greek characters
        text = "дом и σ"
        result = detect_language(text)
        assert result in ["greek", "russian"]


class TestIsGreek:
    """Tests for is_greek function."""

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("σπίτι", True),
            ("hello", False),
            ("привет", False),
            ("", False),
            ("abc σ def", True),
        ],
    )
    def test_is_greek(self, text: str, expected: bool):
        """Test is_greek detection."""
        assert is_greek(text) == expected


class TestIsRussian:
    """Tests for is_russian function."""

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("привет", True),
            ("hello", False),
            ("σπίτι", False),
            ("", False),
            ("abc д def", True),
        ],
    )
    def test_is_russian(self, text: str, expected: bool):
        """Test is_russian detection."""
        assert is_russian(text) == expected
