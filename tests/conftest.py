"""Pytest configuration and fixtures."""

import os

# Set test environment variables BEFORE importing any bot modules
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test_token_123")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("OPENAI_API_KEY", "test_openai_key_123")
os.environ.setdefault("DEBUG", "True")

import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from bot.database.base import Base


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session.

    Yields:
        Async database session for testing
    """
    # Create in-memory SQLite database for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "telegram_id": 123456789,
        "username": "test_user",
        "first_name": "Test",
        "last_name": "User",
        "language_code": "en",
    }


@pytest.fixture
def sample_deck_data():
    """Sample deck data for testing."""
    return {
        "name": "Test Deck",
        "description": "A test deck for unit testing",
    }


@pytest.fixture
def sample_card_data():
    """Sample card data for testing."""
    return {
        "front": "Γεια σου",
        "back": "Hello",
        "example": "Γεια σου! Τι κάνεις;",
    }
