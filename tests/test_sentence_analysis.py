"""Tests for sentence analysis and feedback feature."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.services.ai_service import AIService
from bot.services.translation_service import SentenceAnalysisResult, TranslationService


class TestAIServiceSentenceAnalysis:
    """Tests for AIService.analyze_and_translate_sentence()."""

    @pytest.mark.asyncio
    async def test_correct_greek_sentence_returns_is_correct_true(self):
        """Test that correct Greek sentence returns is_correct=True."""
        ai_service = AIService()

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"is_correct": true, "error_description": null, '
                    '"corrected_sentence": null, "translation": "I want to go home"}'
                )
            )
        ]

        with patch.object(
            ai_service.client.chat.completions,
            "create",
            new=AsyncMock(return_value=mock_response),
        ):
            result = await ai_service.analyze_and_translate_sentence(
                sentence="Θέλω να πάω σπίτι",
                source_language="greek",
            )

        assert result["is_correct"] is True
        assert result["error_description"] is None
        assert result["corrected_sentence"] is None
        assert result["translation"] == "I want to go home"

    @pytest.mark.asyncio
    async def test_incorrect_greek_sentence_returns_error_details(self):
        """Test that incorrect Greek sentence returns error details."""
        ai_service = AIService()

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"is_correct": false, '
                    '"error_description": "Wrong article usage.", '
                    '"corrected_sentence": "Η γυναίκα είναι καλή", '
                    '"translation": "The woman is good"}'
                )
            )
        ]

        with patch.object(
            ai_service.client.chat.completions,
            "create",
            new=AsyncMock(return_value=mock_response),
        ):
            result = await ai_service.analyze_and_translate_sentence(
                sentence="Ο γυναίκα είναι καλή",
                source_language="greek",
            )

        assert result["is_correct"] is False
        assert result["error_description"] == "Wrong article usage."
        assert result["corrected_sentence"] == "Η γυναίκα είναι καλή"
        assert result["translation"] == "The woman is good"

    @pytest.mark.asyncio
    async def test_correct_russian_sentence_returns_is_correct_true(self):
        """Test that correct Russian sentence returns is_correct=True."""
        ai_service = AIService()

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"is_correct": true, "error_description": null, '
                    '"corrected_sentence": null, "translation": "Αγαπώ την Ελλάδα"}'
                )
            )
        ]

        with patch.object(
            ai_service.client.chat.completions,
            "create",
            new=AsyncMock(return_value=mock_response),
        ):
            result = await ai_service.analyze_and_translate_sentence(
                sentence="Я люблю Грецию",
                source_language="russian",
            )

        assert result["is_correct"] is True
        assert result["translation"] == "Αγαπώ την Ελλάδα"

    @pytest.mark.asyncio
    async def test_incorrect_russian_sentence_returns_error_details(self):
        """Test that incorrect Russian sentence returns error details."""
        ai_service = AIService()

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"is_correct": false, '
                    '"error_description": "Spelling error: любю -> люблю.", '
                    '"corrected_sentence": "Я люблю Грецию", '
                    '"translation": "Αγαπώ την Ελλάδα"}'
                )
            )
        ]

        with patch.object(
            ai_service.client.chat.completions,
            "create",
            new=AsyncMock(return_value=mock_response),
        ):
            result = await ai_service.analyze_and_translate_sentence(
                sentence="Я любю Грецию",
                source_language="russian",
            )

        assert result["is_correct"] is False
        assert "любю" in result["error_description"]
        assert result["corrected_sentence"] == "Я люблю Грецию"

    @pytest.mark.asyncio
    async def test_json_parse_error_falls_back_to_simple_translation(self):
        """Test that JSON parse error falls back to simple translation."""
        ai_service = AIService()

        # First call returns invalid JSON
        mock_response_invalid = MagicMock()
        mock_response_invalid.choices = [MagicMock(message=MagicMock(content="not valid json"))]

        # Fallback translation call
        mock_response_fallback = MagicMock()
        mock_response_fallback.choices = [MagicMock(message=MagicMock(content="Я хочу домой"))]

        with patch.object(
            ai_service.client.chat.completions,
            "create",
            new=AsyncMock(side_effect=[mock_response_invalid, mock_response_fallback]),
        ):
            result = await ai_service.analyze_and_translate_sentence(
                sentence="Θέλω σπίτι",
                source_language="greek",
            )

        # Should fall back to is_correct=True with simple translation
        assert result["is_correct"] is True
        assert result["translation"] == "Я хочу домой"


class TestTranslationServiceAnalyze:
    """Tests for TranslationService.analyze_and_translate_text()."""

    @pytest.mark.asyncio
    async def test_result_structure_is_correct(self, db_session):
        """Test that result has correct structure."""
        trans_service = TranslationService(db_session)

        mock_ai_result = {
            "is_correct": True,
            "error_description": None,
            "corrected_sentence": None,
            "translation": "Test translation",
        }

        with patch.object(
            trans_service.ai_service,
            "analyze_and_translate_sentence",
            new=AsyncMock(return_value=mock_ai_result),
        ):
            result = await trans_service.analyze_and_translate_text(
                sentence="Test sentence",
                source_language="greek",
            )

        assert isinstance(result, SentenceAnalysisResult)
        assert result.original_sentence == "Test sentence"
        assert result.source_language == "greek"
        assert result.is_correct is True
        assert result.error_description is None
        assert result.corrected_sentence is None
        assert result.translation == "Test translation"

    @pytest.mark.asyncio
    async def test_result_with_errors(self, db_session):
        """Test result structure when sentence has errors."""
        trans_service = TranslationService(db_session)

        mock_ai_result = {
            "is_correct": False,
            "error_description": "Test error",
            "corrected_sentence": "Corrected sentence",
            "translation": "Translation",
        }

        with patch.object(
            trans_service.ai_service,
            "analyze_and_translate_sentence",
            new=AsyncMock(return_value=mock_ai_result),
        ):
            result = await trans_service.analyze_and_translate_text(
                sentence="Wrong sentence",
                source_language="russian",
            )

        assert result.is_correct is False
        assert result.error_description == "Test error"
        assert result.corrected_sentence == "Corrected sentence"
        assert result.translation == "Translation"
