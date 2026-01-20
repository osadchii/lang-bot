"""Script to seed the database with test data."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.config.logging_config import get_logger, setup_logging
from bot.database.engine import get_session
from bot.services.card_service import CardService
from bot.services.deck_service import DeckService
from bot.services.user_service import UserService

logger = get_logger(__name__)


async def seed_data():
    """Seed database with test data."""
    setup_logging()

    logger.info("Seeding database with test data...")

    async with get_session() as session:
        user_service = UserService(session)
        deck_service = DeckService(session)
        card_service = CardService(session)

        # Create test user
        user, created = await user_service.get_or_create_user(
            telegram_id=123456789,
            username="test_user",
            first_name="Test",
            last_name="User",
        )

        if created:
            logger.info(f"Created test user: {user.username}")
        else:
            logger.info(f"Test user already exists: {user.username}")

        # Create test deck
        deck = await deck_service.create_deck(
            user_id=user.id,
            name="Basic Greek Vocabulary",
            description="Common Greek words and phrases for beginners",
        )
        logger.info(f"Created deck: {deck.name}")

        # Sample Greek vocabulary
        sample_cards = [
            ("Γεια σου", "Hello", "Γεια σου! Τι κάνεις; - Hello! How are you?"),
            ("Ευχαριστώ", "Thank you", "Ευχαριστώ πολύ! - Thank you very much!"),
            ("Παρακαλώ", "Please / You're welcome", "Παρακαλώ, πες μου. - Please, tell me."),
            ("Καλημέρα", "Good morning", "Καλημέρα σας! - Good morning to you!"),
            ("Καληνύχτα", "Good night", "Καληνύχτα, ύπνους γλυκούς! - Good night, sweet dreams!"),
            ("Ναι", "Yes", "Ναι, συμφωνώ. - Yes, I agree."),
            ("Όχι", "No", "Όχι, δεν θέλω. - No, I don't want."),
            ("Νερό", "Water", "Θέλω ένα ποτήρι νερό. - I want a glass of water."),
            ("Φαγητό", "Food", "Το φαγητό είναι νόστιμο. - The food is delicious."),
            ("Αγάπη", "Love", "Η αγάπη είναι σημαντική. - Love is important."),
        ]

        for front, back, example in sample_cards:
            card = await card_service.create_card(
                deck_id=deck.id, front=front, back=back, example=example
            )
            logger.info(f"Created card: {front} -> {back}")

        logger.info(f"Created {len(sample_cards)} sample cards")

    logger.info("Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_data())
