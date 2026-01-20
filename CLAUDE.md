# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Greek language learning Telegram bot built with:
- **aiogram 3.x** for Telegram bot framework
- **SQLAlchemy 2.0** with async (asyncpg) for PostgreSQL
- **OpenAI API** for AI-powered features
- **SM-2 algorithm** for spaced repetition system

## Documentation

**IMPORTANT**: All project documentation lives in `/docs` directory and is maintained by the **Documentation Agent**.

### Documentation Structure

```
docs/
├── README.md              # Documentation hub
├── architecture/          # System design and architecture
├── api/                   # API reference documentation
├── guides/                # User and setup guides
└── development/           # Developer documentation
```

### Working with Documentation

1. **Reading Documentation**: Start with `/docs/README.md` for navigation
2. **Architecture Info**: See `/docs/architecture/system-overview.md`
3. **API Reference**: Check `/docs/api/` for service and repository APIs
4. **Development Workflow**: Read `/docs/development/documentation-workflow.md`

### Documentation Agent

A specialized subagent maintains all documentation. To invoke:

```bash
# Automatic - triggers on code changes
# Manual invocation
/docs [command]

# Examples
/docs update          # Update all documentation
/docs verify          # Verify documentation accuracy
/docs api Services    # Update API docs for services
```

**Key Principles**:
- **Single Source of Truth**: All docs in `/docs`
- **Always Current**: Updated with code changes
- **Comprehensive**: Covers architecture, APIs, guides

### When to Update Documentation

Update docs when you:
- ✅ Add new features or services
- ✅ Modify existing APIs or signatures
- ✅ Change architecture or patterns
- ✅ Update dependencies or configuration
- ✅ Fix bugs that affect documented behavior

The Documentation Agent will handle updates automatically, but you can also update manually and commit with code changes.

## Essential Commands

### Running the Bot
```bash
# Development
python -m bot

# With Poetry
poetry run python -m bot
```

### Database Operations
```bash
# Create migration after model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Initialize DB (alternative to migrations)
python scripts/init_db.py

# Seed test data
python scripts/seed_data.py
```

### Testing & Linting
```bash
# Run tests
pytest

# Run specific test
pytest tests/test_core/test_spaced_repetition.py

# Format code (line length: 100)
black bot/

# Lint
ruff check bot/
```

### Database Setup
```bash
# Create database
createdb langbot

# Connect to verify
psql postgresql://user:password@localhost:5432/langbot
```

## Architecture

### Layered Structure (Critical Pattern)

The codebase follows strict layered architecture where **each layer only calls the layer below**:

```
Handlers → Services → Repositories → Models
  (bot/telegram/handlers/)
         ↓
  (bot/services/)
         ↓
  (bot/database/repositories/)
         ↓
  (bot/database/models/)
```

**Never violate this**: Handlers should never directly access repositories or models; they must go through services.

### Request Flow with Middlewares

Middlewares execute in **order** (defined in `bot/telegram/bot.py:44-47`):

1. **LoggingMiddleware** - logs all requests
2. **ThrottlingMiddleware** - prevents spam
3. **DatabaseMiddleware** - injects `session` into handler data
4. **UserContextMiddleware** - injects `user` (auto-creates from telegram_id)

Every handler automatically receives:
- `session: AsyncSession` - database session
- `user: User` - current user (from middleware)
- `user_created: bool` - whether user was just created

### Spaced Repetition System (Core Logic)

The SM-2 algorithm lives in `bot/core/spaced_repetition.py`. Key points:

- **Quality ratings**: 0 (Again), 2 (Hard), 3 (Good), 5 (Easy)
- **Card states** stored in Card model: `ease_factor`, `interval`, `repetitions`, `next_review`
- **Never modify SRS fields directly** - always use `calculate_next_review()` function
- Card scheduling happens in `LearningService.process_card_review()` which:
  1. Calls `calculate_next_review()` to get new SRS values
  2. Updates the Card model
  3. Creates a Review record for analytics

### Database Session Management

**Critical**: This project uses async SQLAlchemy. Always:

```python
# ✅ CORRECT - session from middleware
async def handler(message: Message, session: AsyncSession, user: User):
    service = UserService(session)
    # session is managed by middleware, auto-commits on success

# ❌ WRONG - never create sessions manually in handlers
async def handler(message: Message):
    async with get_session() as session:  # NO!
```

Sessions are injected by `DatabaseMiddleware` and automatically commit/rollback. Only create manual sessions in scripts or tests.

### FSM (Finite State Machine) Patterns

Multi-step flows use aiogram FSM. Example: creating a card manually requires 3 states.

**Pattern**:
1. Define states in `bot/telegram/states/`
2. Start flow: `await state.set_state(CardCreation.waiting_for_front)`
3. Store intermediate data: `await state.update_data(front=front)`
4. Retrieve data: `data = await state.get_data()`
5. Clear when done: `await state.clear()`

**Important**: Always clear state after completing or canceling a flow.

### Configuration

All config comes from `.env` via Pydantic Settings (`bot/config/settings.py`).

Required environment variables:
- `TELEGRAM_BOT_TOKEN` - from @BotFather
- `DATABASE_URL` - must be `postgresql+asyncpg://...` (async driver)
- `OPENAI_API_KEY` - for AI features

Access config: `from bot.config.settings import settings`

## Database Models

### Model Relationships
```
User (1) ──→ (N) Deck (1) ──→ (N) Card (1) ──→ (N) Review
  ↓
  └──→ (N) LearningStats
```

All relationships use cascade delete (`ondelete="CASCADE"`).

### SRS Fields on Card Model
- `ease_factor: float` - difficulty multiplier (default 2.5)
- `interval: int` - days until next review
- `repetitions: int` - consecutive correct reviews
- `next_review: datetime` - when card becomes due

**Never manually update these** - use `bot.core.spaced_repetition.calculate_next_review()`.

### TimestampMixin
Models inherit `TimestampMixin` which auto-adds `created_at` and `updated_at` fields.

## Adding New Features

### Adding a New Handler

1. Create handler file in `bot/telegram/handlers/my_feature.py`
2. Create a Router: `router = Router(name="my_feature")`
3. Add handlers with decorators: `@router.message(F.text == "...")` or `@router.callback_query(...)`
4. Register in `bot/telegram/bot.py`:
   - Import handler module
   - Add `dp.include_router(my_feature.router)` before error router

### Adding Database Model Changes

1. Modify model in `bot/database/models/`
2. Create migration: `alembic revision --autogenerate -m "Add feature X"`
3. Review generated migration in `migrations/versions/`
4. Apply: `alembic upgrade head`

**Never skip migrations** - they're required for production deployments.

### Adding AI Features

AI functionality goes through `AIService` (`bot/services/ai_service.py`). Methods:
- `ask_question()` - general Q&A
- `translate_word()` - Greek ↔ English
- `explain_grammar()` - grammar explanations
- `generate_card_from_word()` - create flashcard

All methods handle errors internally and return user-friendly strings.

## Common Patterns

### Creating a Service Method

Services receive session in `__init__` and create repositories:

```python
class MyService:
    def __init__(self, session: AsyncSession):
        self.repo = MyRepository(session)
        self.session = session
```

### Repository Pattern

Repositories extend `BaseRepository[ModelType]` which provides:
- `create(**kwargs)` - create record
- `get_by_id(id)` - fetch by ID
- `update(instance, **kwargs)` - update fields
- `delete(instance)` - delete record

Add custom queries as methods (e.g., `get_due_cards()` in CardRepository).

### Callback Data Format

Inline keyboard callbacks use format: `"action:id:extra"`

Examples:
- `"deck:123"` - view deck 123
- `"learn:456"` - start learning deck 456
- `"quality:3"` - rate card as Good (quality=3)

Parse with: `int(callback.data.split(":")[1])`

## Testing

Test fixtures in `tests/conftest.py` provide:
- `db_session` - in-memory SQLite session for tests
- `sample_user_data`, `sample_deck_data`, `sample_card_data` - test data

Tests use `pytest-asyncio` - mark async tests with `@pytest.mark.asyncio` or rely on `asyncio_mode = "auto"` in config.

## Important Notes

### Async Everywhere
This entire project is async. Always use:
- `async def` for functions
- `await` for I/O operations
- `AsyncSession` for database
- `async with` for sessions
- `asyncio.run()` for entry point

### HTML Parsing
Bot uses HTML parse mode (set in `bot/telegram/bot.py:26`). Messages support:
- `<b>bold</b>`
- `<i>italic</i>`
- `<code>code</code>`

Special chars must be escaped in user content.

### Error Handling
Global error handler in `bot/telegram/handlers/errors.py` catches all unhandled exceptions. It logs errors and notifies users gracefully.

Add specific error handling in services/handlers for expected errors (e.g., card not found).

## File Imports

Due to circular import risks, handlers import services locally within functions or at module level carefully. The pattern in `bot/telegram/bot.py:60-68` imports handlers inside `setup_handlers()` to avoid issues.

## Entry Point

The bot starts via: `python -m bot` which executes `bot/__main__.py`.

Startup sequence:
1. Setup logging (`setup_logging()`)
2. Create bot and dispatcher
3. Register middlewares (in order!)
4. Register handlers
5. Set bot commands
6. Start polling

Shutdown: Gracefully closes database connections (`close_db()`).
