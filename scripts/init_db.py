"""Script to initialize the database."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.config.logging_config import get_logger, setup_logging
from bot.database.base import Base
from bot.database.engine import get_engine
from bot.database.models import Card, Deck, LearningStats, Review, User

logger = get_logger(__name__)


async def init_db():
    """Initialize database by creating all tables."""
    setup_logging()

    logger.info("Initializing database...")

    engine = get_engine()

    async with engine.begin() as conn:
        # Drop all tables (be careful in production!)
        # await conn.run_sync(Base.metadata.drop_all)
        # logger.info("Dropped all tables")

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Created all tables")

    await engine.dispose()

    logger.info("Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(init_db())
