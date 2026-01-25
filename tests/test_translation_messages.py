"""Tests for translation message formatting."""

from bot.messages.translation import get_sentence_feedback_message


class TestGetSentenceFeedbackMessage:
    """Tests for get_sentence_feedback_message()."""

    def test_correct_sentence_message(self):
        """Test message for correct sentence."""
        result = get_sentence_feedback_message(
            is_correct=True,
            translation="This is the translation",
        )

        assert "<b>Правильно!</b>" in result
        assert "This is the translation" in result

    def test_incorrect_sentence_with_error_details(self):
        """Test message for incorrect sentence with full error details."""
        result = get_sentence_feedback_message(
            is_correct=False,
            translation="The translation",
            error_description="Wrong verb conjugation",
            corrected_sentence="Corrected sentence here",
        )

        assert "<b>Ошибка:</b>" in result
        assert "Wrong verb conjugation" in result
        assert "<b>Исправленный вариант:</b>" in result
        assert "Corrected sentence here" in result
        assert "<b>Перевод:</b>" in result
        assert "The translation" in result

    def test_fallback_to_translation_only_when_missing_error_description(self):
        """Test fallback when error_description is missing."""
        result = get_sentence_feedback_message(
            is_correct=False,
            translation="Just translation",
            error_description=None,
            corrected_sentence="Corrected",
        )

        # Should fall back to translation-only format
        assert "<b>Перевод:</b>" in result
        assert "Just translation" in result

    def test_fallback_to_translation_only_when_missing_corrected_sentence(self):
        """Test fallback when corrected_sentence is missing."""
        result = get_sentence_feedback_message(
            is_correct=False,
            translation="Just translation",
            error_description="Some error",
            corrected_sentence=None,
        )

        # Should fall back to translation-only format
        assert "<b>Перевод:</b>" in result
        assert "Just translation" in result

    def test_html_escaping_in_translation(self):
        """Test that translation is HTML escaped."""
        result = get_sentence_feedback_message(
            is_correct=True,
            translation="<script>alert('xss')</script>",
        )

        assert "&lt;script&gt;" in result
        assert "<script>" not in result

    def test_html_escaping_in_error_description(self):
        """Test that error_description is HTML escaped."""
        result = get_sentence_feedback_message(
            is_correct=False,
            translation="Translation",
            error_description="Error with <b>bold</b>",
            corrected_sentence="Corrected",
        )

        assert "&lt;b&gt;" in result

    def test_html_escaping_in_corrected_sentence(self):
        """Test that corrected_sentence is HTML escaped."""
        result = get_sentence_feedback_message(
            is_correct=False,
            translation="Translation",
            error_description="Error",
            corrected_sentence="Corrected with <i>italic</i>",
        )

        assert "&lt;i&gt;" in result

    def test_greek_characters_preserved(self):
        """Test that Greek characters are preserved."""
        result = get_sentence_feedback_message(
            is_correct=True,
            translation="Αγαπώ την Ελλάδα",
        )

        assert "Αγαπώ την Ελλάδα" in result

    def test_russian_characters_preserved(self):
        """Test that Russian characters are preserved."""
        result = get_sentence_feedback_message(
            is_correct=True,
            translation="Я люблю Грецию",
        )

        assert "Я люблю Грецию" in result
