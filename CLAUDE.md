# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

Greek language learning Telegram bot built with:
- **aiogram 3.x** - Telegram bot framework
- **SQLAlchemy 2.0** with async (asyncpg) - PostgreSQL
- **OpenAI API** - AI-powered features
- **SM-2 algorithm** - Spaced repetition system

## Rules and Guidelines

**CRITICAL**: All development rules are in `.claude/rules/`:

- **[constraints.md](./.claude/rules/constraints.md)** - NON-NEGOTIABLE constraints
- **[architecture.md](./.claude/rules/architecture.md)** - Architecture patterns
- **[development.md](./.claude/rules/development.md)** - Development guidelines
- **[testing.md](./.claude/rules/testing.md)** - Testing requirements
- **[delegation.md](./.claude/rules/delegation.md)** - Agent delegation rules
- **[documentation.md](./.claude/rules/documentation.md)** - Documentation rules
- **[deployment.md](./.claude/rules/deployment.md)** - Deployment procedures

**READ THESE FILES BEFORE MAKING CHANGES**.

## Documentation

All project documentation is in `/docs`:
- Start with [/docs/README.md](./docs/README.md)
- Architecture: [/docs/architecture/system-overview.md](./docs/architecture/system-overview.md)
- API Reference: [/docs/api/](./docs/api/)

### Documentation Agent

```bash
/docs update          # Update all documentation
/docs verify          # Verify accuracy
/docs api Services    # Update service API docs
```

## Essential Commands

### Run Bot
```bash
python -m bot
```

### Database
```bash
alembic revision --autogenerate -m "description"  # Create migration
alembic upgrade head                              # Apply migrations
alembic downgrade -1                              # Rollback
```

### Testing
```bash
pytest                              # Run tests
pytest --cov=bot --cov-report=html  # With coverage
black bot/                          # Format
ruff check bot/                     # Lint
```

## Critical Architecture Rules

### Layer Structure (STRICT)
```
Handlers → Services → Repositories → Models
```

**NEVER skip layers**. See [constraints.md](./.claude/rules/constraints.md).

### Middleware Chain
1. LoggingMiddleware
2. ThrottlingMiddleware
3. DatabaseMiddleware (injects `session`)
4. UserContextMiddleware (injects `user`)

Every handler receives: `session: AsyncSession`, `user: User`, `user_created: bool`

### Spaced Repetition System

- Algorithm: `bot/core/spaced_repetition.py`
- **NEVER** modify SRS fields directly
- Use `calculate_next_review()` function
- Process via `LearningService.process_card_review()`

### Database Sessions

- **NEVER** create sessions manually in handlers
- Use injected `session` from DatabaseMiddleware
- Manual sessions only in scripts/tests

### FSM (Finite State Machine)

1. Define states in `bot/telegram/states/`
2. Start: `await state.set_state(...)`
3. Store: `await state.update_data(...)`
4. Retrieve: `await state.get_data()`
5. **CRITICAL**: `await state.clear()` when done

### Configuration

- All config from `.env` via `bot/config/settings.py`
- Required: `TELEGRAM_BOT_TOKEN`, `DATABASE_URL`, `OPENAI_API_KEY`
- Access: `from bot.config.settings import settings`

## Database Models

### Relationships
```
User (1) → (N) Deck (1) → (N) Card (1) → (N) Review
  ↓
  └→ (N) LearningStats
```

### SRS Fields on Card
- `ease_factor`, `interval`, `repetitions`, `next_review`
- **NEVER modify directly** - use `calculate_next_review()`

## Adding Features

### New Handler
1. Create in `bot/telegram/handlers/my_feature.py`
2. Create router: `router = Router(name="my_feature")`
3. Register in `bot/telegram/bot.py`

### Model Changes
1. Modify model in `bot/database/models/`
2. Create migration: `alembic revision --autogenerate -m "..."`
3. Review migration
4. Apply: `alembic upgrade head`

### AI Features
Use `AIService` from `bot/services/ai_service.py`:
- `ask_question()`, `translate_word()`, `explain_grammar()`, `generate_card_from_word()`

## Code Style

- Black formatting (line length: 100)
- Ruff linting
- **NO emojis** in codebase
- **NO commented-out code**
- **NO unused imports/variables**
- Type hints everywhere
- Modern syntax: `str | None` not `Optional[str]`

## Testing

- Use pytest with asyncio_mode = "auto"
- Fixtures in `tests/conftest.py`
- Coverage: 80%+ overall, 100% for core
- Pre-commit: `black`, `ruff`, `pytest --cov`

## Important Patterns

### Async Everywhere
- `async def` for functions
- `await` for I/O operations
- `AsyncSession` for database
- `async with` for context managers

### Error Handling
- Handle expected errors explicitly
- Let global handler catch unexpected errors
- Never silent error swallowing
- User-friendly messages only

### HTML Formatting
- Bot uses HTML parse mode
- Escape user content: `html.escape()`
- Tags: `<b>`, `<i>`, `<code>`, `<pre>`, `<a>`

### Callback Data
- Format: `"action:id:extra"`
- Parse: `callback.data.split(":")`

## Entry Point

```bash
python -m bot  # Executes bot/__main__.py
```

Startup: Logging → Bot/Dispatcher → Middlewares → Handlers → Commands → Polling

---

**For detailed rules, see `.claude/rules/*.md`**
