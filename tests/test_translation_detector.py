"""Tests for translation request detection."""

import pytest

from bot.utils.translation_detector import detect_translation_request


class TestDetectTranslationRequest:
    """Tests for detect_translation_request function."""

    @pytest.mark.parametrize(
        "text,expected_word,expected_lang",
        [
            ("как переводится дом?", "дом", "russian"),
            ("как переводится σπίτι", "σπίτι", "greek"),
            ("Как переводится кошка", "кошка", "russian"),
        ],
    )
    def test_pattern_kak_perevoditsya(self, text: str, expected_word: str, expected_lang: str):
        """Test 'как переводится X' pattern."""
        result = detect_translation_request(text)
        assert result is not None
        assert result.word == expected_word
        assert result.source_language == expected_lang

    @pytest.mark.parametrize(
        "text,expected_word,expected_lang",
        [
            ("переведи дом", "дом", "russian"),
            ("переведи σπίτι", "σπίτι", "greek"),
            ("Переведи кошка", "кошка", "russian"),
        ],
    )
    def test_pattern_perevedi(self, text: str, expected_word: str, expected_lang: str):
        """Test 'переведи X' pattern."""
        result = detect_translation_request(text)
        assert result is not None
        assert result.word == expected_word
        assert result.source_language == expected_lang

    @pytest.mark.parametrize(
        "text,expected_word,expected_lang",
        [
            ("что значит дом?", "дом", "russian"),
            ("что значит σπίτι", "σπίτι", "greek"),
            ("Что значит привет", "привет", "russian"),
        ],
    )
    def test_pattern_chto_znachit(self, text: str, expected_word: str, expected_lang: str):
        """Test 'что значит X' pattern."""
        result = detect_translation_request(text)
        assert result is not None
        assert result.word == expected_word
        assert result.source_language == expected_lang

    @pytest.mark.parametrize(
        "text,expected_word,expected_lang",
        [
            ("добавь в карточки сидеть", "сидеть", "russian"),
            ("добавь в карточки σπίτι", "σπίτι", "greek"),
            ("Добавь в карточки бежать", "бежать", "russian"),
            ("добавь в карточки καλημέρα", "καλημέρα", "greek"),
        ],
    )
    def test_pattern_dobav_v_kartochki(self, text: str, expected_word: str, expected_lang: str):
        """Test 'добавь в карточки X' pattern."""
        result = detect_translation_request(text)
        assert result is not None
        assert result.word == expected_word
        assert result.source_language == expected_lang

    @pytest.mark.parametrize(
        "text,expected_word,expected_lang",
        [
            ("добавь сидеть в карточки", "сидеть", "russian"),
            ("добавь σπίτι в карточки", "σπίτι", "greek"),
            ("Добавь бежать в карточки", "бежать", "russian"),
        ],
    )
    def test_pattern_dobav_x_v_kartochki(self, text: str, expected_word: str, expected_lang: str):
        """Test 'добавь X в карточки' pattern."""
        result = detect_translation_request(text)
        assert result is not None
        assert result.word == expected_word
        assert result.source_language == expected_lang

    @pytest.mark.parametrize(
        "text,expected_word,expected_lang",
        [
            ("добавь карточку сидеть", "сидеть", "russian"),
            ("добавь карточку σπίτι", "σπίτι", "greek"),
            ("Добавь карточку бежать", "бежать", "russian"),
        ],
    )
    def test_pattern_dobav_kartochku(self, text: str, expected_word: str, expected_lang: str):
        """Test 'добавь карточку X' pattern."""
        result = detect_translation_request(text)
        assert result is not None
        assert result.word == expected_word
        assert result.source_language == expected_lang

    @pytest.mark.parametrize(
        "text,expected_word,expected_lang",
        [
            ("запомни сидеть", "сидеть", "russian"),
            ("запомни σπίτι", "σπίτι", "greek"),
            ("Запомни кошка", "кошка", "russian"),
        ],
    )
    def test_pattern_zapomni(self, text: str, expected_word: str, expected_lang: str):
        """Test 'запомни X' pattern."""
        result = detect_translation_request(text)
        assert result is not None
        assert result.word == expected_word
        assert result.source_language == expected_lang

    @pytest.mark.parametrize(
        "text,expected_word,expected_lang",
        [
            ("сохрани сидеть", "сидеть", "russian"),
            ("сохрани σπίτι", "σπίτι", "greek"),
            ("Сохрани кошка", "кошка", "russian"),
        ],
    )
    def test_pattern_sohrani(self, text: str, expected_word: str, expected_lang: str):
        """Test 'сохрани X' pattern."""
        result = detect_translation_request(text)
        assert result is not None
        assert result.word == expected_word
        assert result.source_language == expected_lang

    @pytest.mark.parametrize(
        "text,expected_word,expected_lang",
        [
            ("добавь ухо", "ухо", "russian"),
            ("добавь σπίτι", "σπίτι", "greek"),
            ("Добавь кошка", "кошка", "russian"),
            ("добавь καλημέρα", "καλημέρα", "greek"),
        ],
    )
    def test_pattern_dobav_simple(self, text: str, expected_word: str, expected_lang: str):
        """Test simple 'добавь X' pattern."""
        result = detect_translation_request(text)
        assert result is not None
        assert result.word == expected_word
        assert result.source_language == expected_lang


class TestSingleWordDetection:
    """Tests for single word translation request detection."""

    @pytest.mark.parametrize(
        "text,expected_lang",
        [
            ("дом", "russian"),
            ("кошка", "russian"),
            ("привет", "russian"),
        ],
    )
    def test_single_russian_word(self, text: str, expected_lang: str):
        """Test detection of single Russian words."""
        result = detect_translation_request(text)
        assert result is not None
        assert result.word == text
        assert result.source_language == expected_lang

    @pytest.mark.parametrize(
        "text,expected_lang",
        [
            ("σπίτι", "greek"),
            ("καλημέρα", "greek"),
            ("γάτα", "greek"),
        ],
    )
    def test_single_greek_word(self, text: str, expected_lang: str):
        """Test detection of single Greek words."""
        result = detect_translation_request(text)
        assert result is not None
        assert result.word == text
        assert result.source_language == expected_lang


class TestNoMatch:
    """Tests for cases where no translation request is detected."""

    @pytest.mark.parametrize(
        "text",
        [
            "",
            "   ",
            "hello world",
            "some random text",
            "12345",
            "/command",
            "a",  # Too short
        ],
    )
    def test_no_match(self, text: str):
        """Test that non-matching text returns None."""
        result = detect_translation_request(text)
        assert result is None

    def test_unknown_language_word(self):
        """Test that English single word is not detected."""
        result = detect_translation_request("hello")
        assert result is None


class TestEdgeCases:
    """Tests for edge cases."""

    def test_word_with_quotes(self):
        """Test pattern with quoted word."""
        result = detect_translation_request("переведи 'дом'")
        assert result is not None
        assert result.word == "дом"

    def test_word_with_double_quotes(self):
        """Test pattern with double quoted word."""
        result = detect_translation_request('переведи "дом"')
        assert result is not None
        assert result.word == "дом"

    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        result = detect_translation_request("  добавь в карточки сидеть  ")
        assert result is not None
        assert result.word == "сидеть"

    def test_case_insensitivity(self):
        """Test case insensitivity."""
        result = detect_translation_request("ДОБАВЬ В КАРТОЧКИ СИДЕТЬ")
        assert result is not None
        assert result.word == "СИДЕТЬ"
