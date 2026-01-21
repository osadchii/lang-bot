"""Message categorization types and structures."""

from dataclasses import dataclass
from enum import Enum

# Confidence thresholds for categorization
CONFIDENCE_HIGH = 0.8  # High confidence, proceed without logging
CONFIDENCE_MEDIUM = 0.7  # Default threshold for is_confident()
CONFIDENCE_LOW = 0.6  # Low confidence, log for monitoring
CONFIDENCE_FALLBACK = 0.5  # Fallback categorization confidence


class MessageCategory(Enum):
    """Categories for user message intent."""

    WORD_TRANSLATION = "word_translation"
    TEXT_TRANSLATION = "text_translation"
    LANGUAGE_QUESTION = "language_question"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class WordTranslationIntent:
    """Intent data for word translation requests.

    Attributes:
        word: The word to translate (cleaned, without command phrases)
        source_language: Detected source language ('greek' or 'russian')
    """

    word: str
    source_language: str  # 'greek' or 'russian'


@dataclass(frozen=True)
class TextTranslationIntent:
    """Intent data for text/sentence translation requests.

    Attributes:
        text: The text to translate
        source_language: Detected source language ('greek' or 'russian')
    """

    text: str
    source_language: str  # 'greek' or 'russian'


@dataclass(frozen=True)
class LanguageQuestionIntent:
    """Intent data for language-related questions.

    Attributes:
        question: The user's question (may be rephrased for clarity)
        topic: Optional topic hint (grammar, vocabulary, pronunciation, etc.)
    """

    question: str
    topic: str | None = None


@dataclass(frozen=True)
class CategorizationResult:
    """Result of message categorization.

    Attributes:
        category: The determined message category
        confidence: AI confidence level (0.0 to 1.0)
        intent: Category-specific intent data (one of the Intent types)
        raw_message: Original user message
    """

    category: MessageCategory
    confidence: float
    intent: WordTranslationIntent | TextTranslationIntent | LanguageQuestionIntent | None
    raw_message: str

    def is_confident(self, threshold: float = CONFIDENCE_MEDIUM) -> bool:
        """Check if categorization confidence meets threshold.

        Args:
            threshold: Minimum confidence level (default CONFIDENCE_MEDIUM)

        Returns:
            True if confidence >= threshold
        """
        return self.confidence >= threshold
