# CLAUDE.md

Guidance for Claude Code when working with this repository.

## Project Overview

Greek language learning Telegram bot for **Russian-speaking users**:
- **aiogram 3.x** + **SQLAlchemy 2.0** async (asyncpg) + **OpenAI API**
- **SM-2 algorithm** for spaced repetition
- **Card format**: Greek (front with article) / Russian (back)

## Rules

All rules in `.claude/rules/`:
- **constraints.md** - NON-NEGOTIABLE (layer separation, SRS, sessions)
- **architecture.md** - Layers, middleware, FSM, routers
- **development.md** - Code style, async, error handling
- **testing.md** - Coverage, fixtures, patterns
- **delegation.md** - Agent workflows
- **documentation.md** - Docs structure
- **deployment.md** - Migrations, CI/CD

**Read before making changes.**

## Commands

```bash
make verify      # Full check before push
make fix         # Auto-fix lint/format
python -m bot    # Run bot
alembic upgrade head  # Apply migrations
```

## Key Patterns

**Layer structure**: `Handlers -> Services -> Repositories -> Models`

**Middleware injects**: `session: AsyncSession`, `user: User`, `user_created: bool`

**SRS**: Never modify card fields directly, use `calculate_next_review()`

**FSM**: Always `await state.clear()` when done

**Config**: `from bot.config.settings import settings`

## Adding Features

- **Handler**: Create in `bot/telegram/handlers/`, register in `bot/telegram/bot.py`
- **Model change**: Create migration with `alembic revision --autogenerate -m "..."`
- **AI**: Use `AIService` methods (`ask_question`, `translate_word`, `generate_card_from_word`)
- **Messages**: All UI text in `bot/messages/`, escape user content with `html.escape()`

## Documentation

All docs in `/docs`. See `docs/README.md` for structure.
