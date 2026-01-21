# System Architecture Overview

## Overview

The Greek Language Learning Bot is built using a **layered architecture** with clear separation of concerns. The system follows modern async Python patterns and integrates Telegram Bot API, PostgreSQL, and OpenAI API.

**Target Audience**: Russian-speaking users learning Greek. All UI and AI responses are in Russian.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Telegram Client                    │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                 aiogram Framework                   │
│              (Bot + Dispatcher)                     │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              Middleware Chain                       │
│  Logging → Throttling → Database → UserContext     │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                   Handlers                          │
│     (Commands, Callbacks, FSM States)              │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                 Service Layer                       │
│    (Business Logic, Orchestration)                 │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              Repository Layer                       │
│         (Data Access Abstraction)                  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                 Database Models                     │
│            (SQLAlchemy ORM)                        │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                PostgreSQL Database                  │
└─────────────────────────────────────────────────────┘
```

## Core Components

### 1. Telegram Bot Layer (`bot/telegram/`)

**Responsibility**: Handle Telegram API interactions

- **bot.py**: Bot initialization, dispatcher setup, middleware registration
- **handlers/**: Message and callback query handlers
- **keyboards/**: Inline and reply keyboard builders
- **states/**: FSM (Finite State Machine) state definitions
- **middlewares/**: Request preprocessing and context injection
- **utils/**: Telegram-specific utilities (callback parsing, etc.)

### 2. Service Layer (`bot/services/`)

**Responsibility**: Business logic and orchestration

Services implement core business logic and coordinate between repositories:

- `UserService`: User management
- `DeckService`: Deck CRUD operations
- `CardService`: Card management
- `LearningService`: Learning sessions, SRS algorithm
- `StatisticsService`: Analytics and reporting
- `AIService`: OpenAI API integration (translations, grammar, card generation, message categorization)
- `ConversationService`: AI conversation history management
- `TranslationService`: Smart translation with card lookup and deck suggestions
- `MessageCategorizationService`: AI-powered message intent detection

**Pattern**: Each service receives `AsyncSession` in `__init__` and creates repositories.

### 3. Repository Layer (`bot/database/repositories/`)

**Responsibility**: Data access abstraction

Repositories provide a clean interface to database operations:

- `UserRepository`: User data access
- `DeckRepository`: Deck queries
- `CardRepository`: Card queries (due cards, new cards, etc.)
- `ReviewRepository`: Review history

**Pattern**: All repositories extend `BaseRepository[ModelType]` which provides:
- `create(**kwargs)`
- `get_by_id(id)`
- `update(instance, **kwargs)`
- `delete(instance)`

### 4. Database Models (`bot/database/models/`)

**Responsibility**: Data structure and relationships

SQLAlchemy ORM models with relationships:

```
User (1) ──→ (N) Deck (1) ──→ (N) Card (1) ──→ (N) Review
  │
  ├──→ (N) LearningStats
  │
  └──→ (N) ConversationMessage
```

All relationships use `ondelete="CASCADE"` for referential integrity.

### 5. Core Logic (`bot/core/`)

**Responsibility**: Domain algorithms

- `spaced_repetition.py`: SM-2 algorithm implementation
- `card_scheduler.py`: Card selection and prioritization
- `constants.py`: Algorithm constants and configuration
- `message_categories.py`: Message categorization types and intents

## Request Flow

### Example: User Reviews a Card

1. **User Input**: User clicks "Learn" button and selects a deck
   ```
   CallbackQuery(data="learn:1")
   ```

2. **Middleware Chain**:
   - `LoggingMiddleware`: Logs the request
   - `ThrottlingMiddleware`: Checks rate limits
   - `DatabaseMiddleware`: Injects `session: AsyncSession`
   - `UserContextMiddleware`: Injects `user: User` (auto-creates if new)

3. **Handler** (`learning.py:show_card_front`):
   - Gets card from session
   - **Randomly selects which side to show** (Greek or Russian)
   - Stores direction in FSM state (`show_front_as_question: bool`)
   - Shows card with direction indicator (`EL -> RU` or `RU -> EL`)

4. **User clicks "Show Answer"**:
   - Handler retrieves stored direction from FSM state
   - Shows the opposite side as the answer
   - Example sentence shown only for Greek->Russian direction

5. **User rates the card** (quality=0, 3, or 5):
   - `LearningService.process_card_review()` called
   - SRS algorithm calculates next review
   - Card updated, next card shown

6. **Response**:
   - Handler sends next card or session summary
   - Middleware commits transaction (auto)

## Middleware Chain Details

Middlewares execute **in order** (defined in `bot/telegram/bot.py:44-47`):

### 1. LoggingMiddleware
- Logs all incoming requests
- Tracks request timing
- Logs user information

### 2. ThrottlingMiddleware
- Prevents spam (0.5s default)
- Memory leak protection (cleanup at 10k entries)
- User feedback when throttled

### 3. DatabaseMiddleware
- Creates `AsyncSession` for request
- Injects `session` into handler data
- Auto-commits on success, rolls back on error

### 4. UserContextMiddleware
- Retrieves or creates user from `telegram_id`
- Injects `user: User` into handler data
- Sets `user_created: bool` flag

**Result**: Every handler receives `session` and `user` automatically.

### Example: User Sends Free-Text Message

The bot uses AI-powered message categorization to handle free-text input:

1. **User Input**: User sends any text message (e.g., "как переводится σπίτι")
   ```
   Message(text="как переводится σπίτι")
   ```

2. **Middleware Chain**: Same as above, injects `session` and `user`

3. **Handler** (`unified_message.py:handle_message`):
   - Checks message is not a command or menu button
   - Shows "thinking" indicator
   - Calls `MessageCategorizationService`

4. **AI Categorization** (`MessageCategorizationService.categorize_message`):
   - Sends message to OpenAI for intent classification
   - Returns `CategorizationResult` with:
     - Category: `WORD_TRANSLATION`, `TEXT_TRANSLATION`, `LANGUAGE_QUESTION`, or `UNKNOWN`
     - Confidence: 0.0-1.0
     - Intent: Extracted data (word, text, or question)
   - Falls back to regex patterns if AI fails

5. **Route to Handler**:
   - `WORD_TRANSLATION`: Translate word, check for existing cards, offer to add
   - `TEXT_TRANSLATION`: Translate sentence/phrase
   - `LANGUAGE_QUESTION`: Answer using AI with conversation history

6. **Translation with Card Check** (for word translation):
   - `TranslationService.translate_with_card_check()`:
     - Calls AIService for translation
     - Searches user's cards for existing entry
     - If not found, suggests appropriate deck or new deck name

7. **Conversation History** (for questions):
   - `ConversationService.get_context_messages()`: Gets recent conversation
   - `AIService.ask_question()`: Answers with context
   - Stores response in conversation history

## Design Patterns

### 1. Layered Architecture

**Rule**: Each layer only calls the layer below
```
Handlers → Services → Repositories → Models
```

❌ **Never**: Handlers calling repositories directly
❌ **Never**: Handlers accessing models directly

### 2. Repository Pattern

Abstracts data access:
```python
# Service layer doesn't know SQL
deck = await deck_repo.get_by_id(deck_id)
cards = await card_repo.get_due_cards(deck_id)
```

### 3. Dependency Injection

Services receive dependencies via constructor:
```python
class LearningService:
    def __init__(self, session: AsyncSession):
        self.card_repo = CardRepository(session)
        self.review_repo = ReviewRepository(session)
        self.session = session
```

### 4. FSM (Finite State Machine)

Multi-step flows use aiogram FSM:
```python
# Define states
class CardCreation(StatesGroup):
    waiting_for_front = State()
    waiting_for_back = State()
    waiting_for_example = State()

# Use in handlers
await state.set_state(CardCreation.waiting_for_front)
data = await state.get_data()
await state.clear()
```

## Technology Stack

### Backend
- **Python 3.11+**: Modern async features
- **aiogram 3.x**: Telegram Bot framework
- **SQLAlchemy 2.0**: Async ORM
- **asyncpg**: PostgreSQL async driver
- **Alembic**: Database migrations
- **OpenAI SDK**: AI integration

### Database
- **PostgreSQL**: Relational database
- **Composite indexes**: Performance optimization
- **CHECK constraints**: Data integrity
- **UNIQUE constraints**: Business rules enforcement

### Development
- **pytest**: Testing framework
- **black**: Code formatting
- **ruff**: Linting
- **poetry**: Dependency management

## Configuration Management

All configuration via environment variables using Pydantic Settings:

```python
# bot/config/settings.py
class Settings(BaseSettings):
    telegram_bot_token: str
    database_url: str
    openai_api_key: str
    # ... more settings
```

Access globally:
```python
from bot.config.settings import settings
```

## Database Session Management

**Critical**: This project uses async SQLAlchemy.

✅ **CORRECT** - Session from middleware:
```python
async def handler(message: Message, session: AsyncSession, user: User):
    service = UserService(session)
    # session managed by middleware
```

❌ **WRONG** - Manual session creation in handlers:
```python
async def handler(message: Message):
    async with get_session() as session:  # NO!
        ...
```

Sessions are injected by `DatabaseMiddleware` and automatically commit/rollback.

## Error Handling

### Global Error Handler
Located in `bot/telegram/handlers/errors.py`, catches all unhandled exceptions.

### Specific Error Handling
- **OpenAI API**: Specific exception types (RateLimitError, APITimeoutError, etc.)
- **Database**: Transaction rollback on error
- **Validation**: ValueError for invalid input

## Security Considerations

1. **Environment Variables**: Secrets in `.env` (never committed)
2. **SQL Injection**: Prevented by ORM parameter binding
3. **Rate Limiting**: Throttling middleware
4. **Input Validation**: Safe callback parsing, data validation
5. **Database Constraints**: Enforce data integrity

## Performance Optimizations

1. **Composite Indexes**:
   - `(deck_id, next_review)` on cards
   - `(deck_id, repetitions)` on cards
   - `(user_id, deck_id, date)` on learning_stats

2. **Async Operations**:
   - Parallel database queries with `asyncio.gather()`
   - Example: `get_deck_stats()` runs 3 queries concurrently

3. **Connection Pooling**:
   - Configured pool size and overflow
   - Pool timeout settings

4. **Memory Management**:
   - Throttling middleware cleanup at 10k entries
   - Old entries purged after 1 hour

## Spaced Repetition System

The bot uses the **SM-2 algorithm** for optimal card scheduling:

### SRS Fields (Card model)
- `ease_factor`: Difficulty multiplier (default 2.5, min 1.3)
- `interval`: Days until next review
- `repetitions`: Consecutive correct reviews
- `next_review`: DateTime when card is due

### Quality Ratings
- 0 = Forgot (completely forgot)
- 3 = Remembered (correct response)
- 5 = Easy (perfect recall)

### Bidirectional Testing

During review, cards are shown with a **random side** as the question:
- **Greek -> Russian** (`EL -> RU`): Shows Greek word, asks for Russian translation
- **Russian -> Greek** (`RU -> EL`): Shows Russian word, asks for Greek translation

The direction is stored in FSM state and the SRS algorithm works identically regardless of direction.

### Algorithm Location
`bot/core/spaced_repetition.py:calculate_next_review()`

**Important**: Never manually update SRS fields - always use the algorithm.

## Deployment Architecture

```
┌─────────────────────┐
│   Telegram Client   │
└─────────────────────┘
          ↓
┌─────────────────────┐
│   Bot Application   │
│   (Python Process)  │
└─────────────────────┘
          ↓
┌─────────────────────┐
│   PostgreSQL DB     │
│   (Docker/Cloud)    │
└─────────────────────┘
          ↓
┌─────────────────────┐
│    OpenAI API       │
│    (External)       │
└─────────────────────┘
```

### Deployment Options
- **Polling**: Default mode, no webhooks needed
- **Webhooks**: For production with reverse proxy
- **Docker**: Containerized deployment (recommended)
- **Cloud**: Heroku, Railway, AWS, etc.

## Extension Points

### Adding a New Feature

1. **Create Model** (if needed): `bot/database/models/`
2. **Create Migration**: `alembic revision --autogenerate`
3. **Create Repository**: `bot/database/repositories/`
4. **Create Service**: `bot/services/`
5. **Create Handler**: `bot/telegram/handlers/`
6. **Register Handler**: `bot/telegram/bot.py`
7. **Update Documentation**: You're here! 📝

### Adding AI Features

Extend `AIService` in `bot/services/ai_service.py`:
- Methods handle errors internally
- Return user-friendly strings
- Use configured timeout

## Further Reading

- [Database Schema](./database-schema.md) - Detailed model documentation
- [Middleware Chain](./middleware-chain.md) - Middleware details
- [Service Layer](./service-layer.md) - Service patterns
- [API Reference](../api/services.md) - Service API docs

---

**Last Updated**: 2026-01-21
**Maintained by**: Documentation Agent
