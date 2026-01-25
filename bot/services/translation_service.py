"""Translation service for smart translation with card lookup."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.card import Card
from bot.database.models.deck import Deck
from bot.database.models.user import User
from bot.database.repositories.card_repo import CardRepository
from bot.database.repositories.deck_repo import DeckRepository
from bot.services.ai_service import AIService


@dataclass
class TranslationResult:
    """Result of a translation request."""

    word: str
    source_language: str  # 'greek' or 'russian'
    translation: str  # AI translation response
    existing_card: Card | None = None  # Found card if exists
    existing_deck: Deck | None = None  # Deck containing the card
    existing_count: int = 0  # Number of decks containing the word
    suggested_deck: Deck | None = None  # AI-suggested deck for new card
    suggested_deck_name: str | None = None  # Suggested name if no suitable deck


@dataclass
class CardData:
    """Data for creating a card from translation."""

    front: str  # Greek with article
    back: str  # Russian
    example: str


@dataclass
class SentenceAnalysisResult:
    """Result of sentence analysis with feedback."""

    original_sentence: str
    source_language: str
    is_correct: bool
    error_description: str | None
    corrected_sentence: str | None
    translation: str


class TranslationService:
    """Service for smart translations with card awareness."""

    def __init__(self, session: AsyncSession):
        """Initialize translation service.

        Args:
            session: Database session
        """
        self.session = session
        self.ai_service = AIService()
        self.card_repo = CardRepository(session)
        self.deck_repo = DeckRepository(session)

    async def translate_with_card_check(
        self,
        user: User,
        word: str,
        source_language: str,
    ) -> TranslationResult:
        """Translate word and check if it exists in user's cards.

        Args:
            user: User making the request
            word: Word to translate
            source_language: 'greek' or 'russian'

        Returns:
            TranslationResult with all relevant data
        """
        # Determine translation direction
        if source_language == "greek":
            from_lang, to_lang = "greek", "russian"
        else:
            from_lang, to_lang = "russian", "greek"

        # Get translation from AI
        translation = await self.ai_service.translate_word(word, from_lang, to_lang)

        # Search for existing cards
        existing_cards = await self.card_repo.search_user_cards(user.id, word)

        if existing_cards:
            # Card exists - get the first match and deck
            card, deck_id = existing_cards[0]
            deck = await self.deck_repo.get_by_id(deck_id)
            return TranslationResult(
                word=word,
                source_language=source_language,
                translation=translation,
                existing_card=card,
                existing_deck=deck,
                existing_count=len(existing_cards),
            )

        # No existing card - suggest a deck
        decks = await self.deck_repo.get_user_decks(user.id)
        deck_names = [d.name for d in decks]

        # Get AI suggestion for best deck
        suggested_name = await self.ai_service.suggest_deck_for_word(word, translation, deck_names)

        suggested_deck = None
        suggested_new_name = None

        if suggested_name:
            # Find the deck by name
            for deck in decks:
                if deck.name == suggested_name:
                    suggested_deck = deck
                    break
        else:
            # No suitable deck - generate a new deck name
            suggested_new_name = await self.ai_service.generate_deck_name(word, translation)

        return TranslationResult(
            word=word,
            source_language=source_language,
            translation=translation,
            suggested_deck=suggested_deck,
            suggested_deck_name=suggested_new_name,
        )

    async def generate_card_data(self, word: str, source_language: str) -> CardData:
        """Generate card data from a word.

        Args:
            word: Word to create card from
            source_language: 'greek' or 'russian'

        Returns:
            CardData with front, back, and example
        """
        card_dict = await self.ai_service.generate_card_from_word(word, source_language)
        return CardData(
            front=card_dict.get("front", word),
            back=card_dict.get("back", ""),
            example=card_dict.get("example", ""),
        )

    async def analyze_and_translate_text(
        self,
        sentence: str,
        source_language: str,
    ) -> SentenceAnalysisResult:
        """Analyze sentence for errors and translate.

        Args:
            sentence: Sentence to analyze
            source_language: 'greek' or 'russian'

        Returns:
            SentenceAnalysisResult with analysis and translation
        """
        result = await self.ai_service.analyze_and_translate_sentence(sentence, source_language)

        return SentenceAnalysisResult(
            original_sentence=sentence,
            source_language=source_language,
            is_correct=result.get("is_correct", True),
            error_description=result.get("error_description"),
            corrected_sentence=result.get("corrected_sentence"),
            translation=result.get("translation", ""),
        )
