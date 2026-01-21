"""Service for AI-powered message categorization."""

from bot.config.logging_config import get_logger
from bot.core.message_categories import (
    CONFIDENCE_FALLBACK,
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    CategorizationResult,
    LanguageQuestionIntent,
    MessageCategory,
    TextTranslationIntent,
    WordTranslationIntent,
)
from bot.services.ai_service import AIService
from bot.utils.language_detector import detect_language

logger = get_logger(__name__)


class MessageCategorizationService:
    """Service for categorizing user messages using AI."""

    def __init__(self):
        """Initialize categorization service."""
        self.ai_service = AIService()

    async def categorize_message(self, message: str) -> CategorizationResult:
        """Categorize a user message using AI.

        Args:
            message: User's message text

        Returns:
            CategorizationResult with category, confidence, and intent data
        """
        message = message.strip()

        if not message:
            return CategorizationResult(
                category=MessageCategory.UNKNOWN,
                confidence=1.0,
                intent=None,
                raw_message=message,
            )

        # Try AI categorization
        try:
            ai_result = await self.ai_service.categorize_message(message)
            return self._parse_ai_result(ai_result, message)
        except Exception as e:
            logger.warning(f"AI categorization failed, using fallback: {e}")
            return self._fallback_categorization(message)

    def _parse_ai_result(self, ai_result: dict, raw_message: str) -> CategorizationResult:
        """Parse AI categorization result into structured format.

        Args:
            ai_result: Parsed JSON from AI response
            raw_message: Original user message

        Returns:
            CategorizationResult with appropriate intent
        """
        category_str = ai_result.get("category", "unknown")
        confidence = float(ai_result.get("confidence", 0.5))
        extracted = ai_result.get("extracted_content", raw_message)
        source_lang = ai_result.get("source_language")
        topic = ai_result.get("topic")

        try:
            category = MessageCategory(category_str)
        except ValueError:
            category = MessageCategory.UNKNOWN

        intent = self._build_intent(category, extracted, source_lang, topic)

        return CategorizationResult(
            category=category,
            confidence=confidence,
            intent=intent,
            raw_message=raw_message,
        )

    def _build_intent(
        self,
        category: MessageCategory,
        content: str,
        source_lang: str | None,
        topic: str | None,
    ) -> WordTranslationIntent | TextTranslationIntent | LanguageQuestionIntent | None:
        """Build appropriate intent object based on category.

        Args:
            category: Message category
            content: Extracted content from message
            source_lang: Detected source language
            topic: Question topic (for language questions)

        Returns:
            Intent object or None for unknown category
        """
        if category == MessageCategory.LANGUAGE_QUESTION:
            return LanguageQuestionIntent(question=content, topic=topic)

        if category == MessageCategory.UNKNOWN:
            return None

        # Validate/detect source language for translation categories
        validated_lang = self._validate_language(source_lang, content)

        if category == MessageCategory.WORD_TRANSLATION:
            return WordTranslationIntent(word=content, source_language=validated_lang)

        if category == MessageCategory.TEXT_TRANSLATION:
            return TextTranslationIntent(text=content, source_language=validated_lang)

        return None

    def _validate_language(self, source_lang: str | None, content: str) -> str:
        """Validate and detect source language.

        Args:
            source_lang: Language provided by AI
            content: Content to detect language from

        Returns:
            Validated language string ('greek' or 'russian')
        """
        if source_lang in ("greek", "russian"):
            return source_lang

        detected = detect_language(content)
        return detected if detected in ("greek", "russian") else "russian"

    def _fallback_categorization(self, message: str) -> CategorizationResult:
        """Fallback categorization using simple heuristics.

        Used when AI categorization fails. Preserves backward compatibility
        with the old regex-based approach.

        Args:
            message: User message

        Returns:
            CategorizationResult based on simple rules
        """
        from bot.utils.translation_detector import detect_translation_request

        # Try existing pattern detection
        translation_request = detect_translation_request(message)
        if translation_request:
            return CategorizationResult(
                category=MessageCategory.WORD_TRANSLATION,
                confidence=CONFIDENCE_HIGH,
                intent=WordTranslationIntent(
                    word=translation_request.word,
                    source_language=translation_request.source_language,
                ),
                raw_message=message,
            )

        # Check if it looks like a question
        question_indicators = ["?", "как", "почему", "когда", "зачем", "что такое"]
        is_question = any(ind in message.lower() for ind in question_indicators)

        if is_question:
            return CategorizationResult(
                category=MessageCategory.LANGUAGE_QUESTION,
                confidence=CONFIDENCE_LOW,
                intent=LanguageQuestionIntent(question=message),
                raw_message=message,
            )

        # Default: try to translate as text
        lang = detect_language(message)
        return CategorizationResult(
            category=MessageCategory.TEXT_TRANSLATION,
            confidence=CONFIDENCE_FALLBACK,
            intent=TextTranslationIntent(
                text=message,
                source_language=lang if lang in ("greek", "russian") else "russian",
            ),
            raw_message=message,
        )
