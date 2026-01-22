"""Service for extracting vocabulary from phrases."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from bot.config.logging_config import get_logger
from bot.database.models.user import User
from bot.database.repositories.card_repo import CardRepository
from bot.services.ai_service import AIService

logger = get_logger(__name__)


@dataclass
class ExtractedWord:
    """A word extracted from phrase, ready for card creation."""

    original_form: str  # Form as it appeared in the phrase
    lemma: str  # Base/dictionary form (lowercase)
    lemma_with_article: str  # For nouns: "o/h/to lemma"
    translation: str  # Russian translation
    part_of_speech: str  # noun, verb, adjective, adverb, etc.
    already_in_cards: bool = False  # True if user already has this word


@dataclass
class VocabularyExtractionResult:
    """Result of vocabulary extraction from a phrase."""

    phrase: str  # Original phrase
    phrase_translation: str  # Translation of full phrase
    source_language: str  # 'greek' or 'russian'
    extracted_words: list[ExtractedWord]  # All extracted content words
    new_words: list[ExtractedWord]  # Words not in user's cards
    existing_words: list[ExtractedWord]  # Words already in cards


class VocabularyExtractionService:
    """Service for extracting learnable vocabulary from phrases."""

    def __init__(self, session: AsyncSession):
        """Initialize vocabulary extraction service.

        Args:
            session: Async database session
        """
        self.session = session
        self.ai_service = AIService()
        self.card_repo = CardRepository(session)

    async def extract_vocabulary(
        self,
        user: User,
        phrase: str,
        phrase_translation: str,
        source_language: str,
    ) -> VocabularyExtractionResult:
        """Extract learnable vocabulary from a translated phrase.

        Args:
            user: User instance
            phrase: Original phrase
            phrase_translation: Translation of the phrase
            source_language: 'greek' or 'russian'

        Returns:
            VocabularyExtractionResult with all extracted words
        """
        # Use AI to extract and lemmatize words
        ai_result = await self.ai_service.extract_and_lemmatize_words(
            phrase=phrase,
            source_language=source_language,
        )

        if not ai_result:
            return VocabularyExtractionResult(
                phrase=phrase,
                phrase_translation=phrase_translation,
                source_language=source_language,
                extracted_words=[],
                new_words=[],
                existing_words=[],
            )

        # Build extracted words list
        extracted_words = []
        for word_data in ai_result:
            extracted = ExtractedWord(
                original_form=word_data.get("original", ""),
                lemma=word_data.get("lemma", "").lower(),
                lemma_with_article=word_data.get(
                    "lemma_with_article", word_data.get("lemma", "")
                ).lower(),
                translation=word_data.get("translation", ""),
                part_of_speech=word_data.get("pos", "unknown"),
                already_in_cards=False,
            )
            extracted_words.append(extracted)

        # Bulk check against user's cards
        await self._check_cards(user.id, extracted_words)

        # Separate new and existing words
        new_words = [w for w in extracted_words if not w.already_in_cards]
        existing_words = [w for w in extracted_words if w.already_in_cards]

        return VocabularyExtractionResult(
            phrase=phrase,
            phrase_translation=phrase_translation,
            source_language=source_language,
            extracted_words=extracted_words,
            new_words=new_words,
            existing_words=existing_words,
        )

    async def _check_cards(
        self,
        user_id: int,
        words: list[ExtractedWord],
    ) -> None:
        """Check which words exist in user's cards (mutates words in place).

        Args:
            user_id: User ID
            words: List of extracted words to check
        """
        if not words:
            return

        # Get all lemmas to search for
        lemmas = []
        for w in words:
            lemmas.append(w.lemma)
            if w.lemma_with_article != w.lemma:
                lemmas.append(w.lemma_with_article)

        # Bulk search
        found_cards = await self.card_repo.find_cards_by_lemmas(user_id, lemmas)

        # Create lookup set from found cards
        found_lemmas: set[str] = set()
        for card, _ in found_cards:
            found_lemmas.add(card.front.lower())
            found_lemmas.add(card.back.lower())

        # Update words (lemmas are already lowercase)
        for word in words:
            if word.lemma in found_lemmas or word.lemma_with_article in found_lemmas:
                word.already_in_cards = True
