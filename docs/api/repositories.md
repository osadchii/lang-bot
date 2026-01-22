# Repositories API Reference

## Overview

Repositories provide a clean data access abstraction layer. All repositories extend `BaseRepository[ModelType]` which provides standard CRUD operations.

**Important**: Repositories should only be used by Services, never directly by Handlers.

## BaseRepository

**File**: `bot/database/repositories/base.py`

Generic base class providing standard CRUD operations.

### Methods

#### `create(**kwargs) -> Model`
Create a new model instance.

#### `get_by_id(id: int) -> Model | None`
Get model by ID.

#### `update(instance: Model, **kwargs) -> Model`
Update model instance.

#### `delete(instance: Model) -> None`
Delete model instance.

---

## CardRepository

**File**: `bot/database/repositories/card_repo.py`

Repository for Card model operations.

### Methods

#### `get_deck_cards(deck_id: int, limit: int = None, offset: int = 0) -> list[Card]`

Get all cards in a deck with optional pagination.

#### `get_due_cards(deck_id: int, limit: int = None, current_time: datetime = None) -> list[Card]`

Get cards that are due for review, ordered by next_review (oldest first).

#### `get_new_cards(deck_id: int, limit: int = None) -> list[Card]`

Get new cards (never reviewed, repetitions=0).

#### `count_due_cards(deck_id: int, current_time: datetime = None) -> int`

Count cards due for review.

#### `count_new_cards(deck_id: int) -> int`

Count new cards in a deck.

#### `search_cards(deck_id: int, search_term: str) -> list[Card]`

Search cards by front or back text within a deck.

#### `search_user_cards(user_id: int, search_term: str, limit: int = 10) -> list[tuple[Card, int]]`

Search all user's cards across all decks. Returns list of (Card, deck_id) tuples.

#### `get_due_cards_from_decks(deck_ids: list[int], limit: int = None, current_time: datetime = None) -> list[Card]`

Get cards due for review from multiple decks.

#### `get_new_cards_from_decks(deck_ids: list[int], limit: int = None) -> list[Card]`

Get new cards from multiple decks.

#### `count_due_cards_from_decks(deck_ids: list[int], current_time: datetime = None) -> int`

Count cards due for review from multiple decks.

#### `count_new_cards_from_decks(deck_ids: list[int]) -> int`

Count new cards from multiple decks.

#### `find_cards_by_lemmas(user_id: int, lemmas: list[str], limit: int = 100) -> list[tuple[Card, int]]`

Find cards matching any of the provided lemmas. Used for bulk vocabulary checking during vocabulary extraction.

**Parameters**:
- `user_id` (int): User ID
- `lemmas` (list[str]): List of lemmas to search for (case-insensitive)
- `limit` (int): Maximum results (default: 100)

**Returns**: List of (Card, deck_id) tuples for matching cards

**Behavior**:
- Searches both `front` and `back` fields
- Case-insensitive exact matching
- Joins with Deck to filter by user

**Example**:
```python
card_repo = CardRepository(session)

# Check if user has any of these words
lemmas = ["σπιτι", "το σπιτι", "μεγαλος", "ειμαι"]
found = await card_repo.find_cards_by_lemmas(
    user_id=1,
    lemmas=lemmas
)

for card, deck_id in found:
    print(f"Found: {card.front} in deck {deck_id}")
```

**Used By**: `VocabularyExtractionService._check_cards()` for determining which extracted words the user already knows.

---

## DeckRepository

**File**: `bot/database/repositories/deck_repo.py`

Repository for Deck model operations.

### Methods

#### `get_user_decks(user_id: int) -> list[Deck]`

Get all decks for a user.

#### `get_deck_by_name(user_id: int, name: str) -> Deck | None`

Get deck by name for a user.

#### `count_cards(deck_id: int) -> int`

Count cards in a deck.

---

## UserRepository

**File**: `bot/database/repositories/user_repo.py`

Repository for User model operations.

### Methods

#### `get_by_telegram_id(telegram_id: int) -> User | None`

Get user by Telegram ID.

---

## ReviewRepository

**File**: `bot/database/repositories/review_repo.py`

Repository for Review model operations.

### Methods

#### `get_card_reviews(card_id: int, limit: int = None) -> list[Review]`

Get review history for a card.

#### `get_user_reviews(user_id: int, limit: int = None) -> list[Review]`

Get review history for a user.

---

## Further Reading

- [Services API](./services.md) - Service layer that uses repositories
- [Database Schema](../architecture/database-schema.md) - Model definitions

---

**Last Updated**: 2026-01-22
**Maintained by**: Documentation Agent
