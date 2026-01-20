# Services API Reference

## Overview

Services contain business logic and orchestrate operations between handlers and repositories. All services follow the same initialization pattern: they receive `AsyncSession` and create necessary repositories.

## Common Pattern

```python
class ServiceName:
    def __init__(self, session: AsyncSession):
        self.repo = SomeRepository(session)
        self.session = session

    async def method_name(self, param: Type) -> ReturnType:
        # Business logic
        pass
```

---

## UserService

**File**: `bot/services/user_service.py`

Manages user accounts and user-related operations.

### Methods

#### `get_or_create_user(telegram_id: int, **kwargs) -> tuple[User, bool]`

Get existing user or create new one.

**Parameters**:
- `telegram_id` (int): Telegram user ID
- `**kwargs`: Additional user fields (username, first_name, language_code)

**Returns**: Tuple of (User, created) where created is bool

**Example**:
```python
from bot.services.user_service import UserService

user_service = UserService(session)
user, was_created = await user_service.get_or_create_user(
    telegram_id=123456789,
    username="john_doe",
    first_name="John"
)
```

---

## DeckService

**File**: `bot/services/deck_service.py`

Handles deck management operations.

### Methods

#### `create_deck(user_id: int, name: str, description: str = None) -> Deck`

Create a new deck for a user.

**Parameters**:
- `user_id` (int): User ID
- `name` (str): Deck name (max 255 chars)
- `description` (str, optional): Deck description

**Returns**: Created Deck instance

**Raises**:
- `ValueError`: If deck name is empty or too long
- `IntegrityError`: If deck with same name already exists for user

**Example**:
```python
deck_service = DeckService(session)
deck = await deck_service.create_deck(
    user_id=1,
    name="Greek Basics",
    description="Essential Greek vocabulary"
)
```

#### `get_user_decks(user_id: int) -> list[Deck]`

Get all decks for a user.

**Example**:
```python
decks = await deck_service.get_user_decks(user_id=1)
```

#### `get_deck_with_stats(deck_id: int) -> tuple[Deck | None, int]`

Get deck with card count.

**Returns**: Tuple of (Deck, card_count)

---

## CardService

**File**: `bot/services/card_service.py`

Manages flashcard operations.

### Methods

#### `create_card(deck_id: int, front: str, back: str, example: str = None, notes: str = None) -> Card`

Create a new flashcard.

**Parameters**:
- `deck_id` (int): Deck to add card to
- `front` (str): Front of card (question/word)
- `back` (str): Back of card (answer/translation)
- `example` (str, optional): Example usage
- `notes` (str, optional): Additional notes

**Returns**: Created Card instance

**Example**:
```python
card_service = CardService(session)
card = await card_service.create_card(
    deck_id=1,
    front="Γεια σου",
    back="Hello (informal)",
    example="Γεια σου, τι κάνεις; - Hello, how are you?"
)
```

#### `get_deck_cards(deck_id: int, limit: int = 100, offset: int = 0) -> list[Card]`

Get cards from a deck with pagination.

---

## LearningService

**File**: `bot/services/learning_service.py`

Handles learning sessions and spaced repetition.

### Methods

#### `get_learning_session(deck_id: int, max_cards: int = 20, max_new_cards: int = 20) -> list[Card]`

Get cards for a learning session.

**Parameters**:
- `deck_id` (int): Deck to learn from
- `max_cards` (int): Maximum total cards (default: 20)
- `max_new_cards` (int): Maximum new cards to include (default: 20)

**Returns**: List of Card instances (mix of due and new cards)

**Example**:
```python
learning_service = LearningService(session)
cards = await learning_service.get_learning_session(
    deck_id=1,
    max_cards=20,
    max_new_cards=10
)
```

#### `process_card_review(card_id: int, user_id: int, quality: int, time_spent: int = None) -> Card`

Process a card review and update SRS data.

**Parameters**:
- `card_id` (int): Card being reviewed
- `user_id` (int): User reviewing the card
- `quality` (int): Quality rating (0, 2, 3, 5)
- `time_spent` (int, optional): Time spent in seconds

**Returns**: Updated Card instance

**Raises**:
- `ValueError`: If card not found or SRS calculation fails

**Example**:
```python
# User rates card as "Good" (3)
card = await learning_service.process_card_review(
    card_id=123,
    user_id=1,
    quality=3,
    time_spent=15
)
print(f"Next review: {card.next_review}")
```

#### `get_deck_stats(deck_id: int) -> dict`

Get statistics for a deck.

**Returns**: Dictionary with:
- `total_cards`: Total number of cards
- `new_cards`: Number of new cards (repetitions=0)
- `due_cards`: Number of cards due for review
- `learning_cards`: Number of cards in learning (total - new)

**Example**:
```python
stats = await learning_service.get_deck_stats(deck_id=1)
print(f"Total: {stats['total_cards']}, Due: {stats['due_cards']}")
```

---

## AIService

**File**: `bot/services/ai_service.py`

OpenAI API integration for AI-powered features.

### Methods

#### `ask_question(message: str, context: str = None) -> str`

Ask a question to the AI assistant.

**Parameters**:
- `message` (str): User's question
- `context` (str, optional): Additional context

**Returns**: AI's response as string

**Example**:
```python
ai_service = AIService()
response = await ai_service.ask_question(
    "What is the difference between και and αλλά?"
)
```

#### `translate_word(word: str, from_lang: str = "greek", to_lang: str = "english") -> str`

Translate a word or phrase.

**Example**:
```python
translation = await ai_service.translate_word("καλημέρα")
# Returns: "Good morning (formal greeting)"
```

#### `explain_grammar(text: str) -> str`

Explain the grammar of Greek text.

**Example**:
```python
explanation = await ai_service.explain_grammar("Το βιβλίο είναι ενδιαφέρον")
```

#### `generate_card_from_word(word: str) -> dict[str, str]`

Generate a flashcard from a Greek word using AI.

**Returns**: Dictionary with keys: `front`, `back`, `example`

**Example**:
```python
card_data = await ai_service.generate_card_from_word("αγάπη")
# Returns: {"front": "αγάπη", "back": "love", "example": "..."}
```

---

## StatisticsService

**File**: `bot/services/statistics_service.py`

Provides analytics and statistics.

### Methods

#### `get_user_stats(user_id: int) -> dict`

Get overall statistics for a user.

**Returns**: Dictionary with various statistics

**Example**:
```python
stats_service = StatisticsService(session)
stats = await stats_service.get_user_stats(user_id=1)
```

---

## Error Handling

All services handle errors appropriately:

### OpenAI Service Errors

```python
try:
    response = await ai_service.ask_question("...")
except Exception as e:
    # Returns user-friendly error message
    # Specific exceptions: RateLimitError, APITimeoutError, etc.
```

### Database Errors

```python
try:
    deck = await deck_service.create_deck(...)
except IntegrityError:
    # Handle duplicate deck name
except ValueError:
    # Handle validation errors
```

## Best Practices

1. **Always use services from handlers** - Never call repositories directly
2. **Pass AsyncSession to constructor** - Services manage their own repositories
3. **Trust service validation** - Services validate input before database operations
4. **Handle returned exceptions** - Services raise meaningful exceptions
5. **Use type hints** - All service methods are fully typed

## Further Reading

- [Repository API](./repositories.md) - Data access layer
- [Service Layer Architecture](../architecture/service-layer.md) - Design patterns
- [Handler Reference](./handlers.md) - How handlers use services

---

**Last Updated**: 2026-01-20
**Maintained by**: Documentation Agent
