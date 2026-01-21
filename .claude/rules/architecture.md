# Architecture Rules

## Layer Structure

```
Handlers → Services → Repositories → Models
```

### Handlers (bot/telegram/handlers/)
- Receive Telegram updates
- Call Services only
- Format responses
- Manage FSM state
- NO business logic

### Services (bot/services/)
- ALL business logic
- Coordinate repositories
- NO Telegram-specific code
- Return data, not Telegram responses

### Repositories (bot/database/repositories/)
- Data access only
- Extend BaseRepository
- NO business logic
- Return SQLAlchemy models

### Models (bot/database/models/)
- Schema definition
- Relationships
- NO methods

## Middleware Chain Order

1. LoggingMiddleware
2. ThrottlingMiddleware
3. DatabaseMiddleware (injects session)
4. UserContextMiddleware (injects user)

## Handler Signature

Every handler receives:
- `session: AsyncSession` (from DatabaseMiddleware)
- `user: User` (from UserContextMiddleware)
- `user_created: bool` (from UserContextMiddleware)

## FSM Pattern

1. Define states in `bot/telegram/states/`
2. `await state.set_state(...)` to start
3. `await state.update_data(...)` to store data
4. `await state.get_data()` to retrieve
5. `await state.clear()` when done (MANDATORY)

## SRS Integration

- Use `calculate_next_review()` from `bot/core/spaced_repetition.py`
- NEVER modify Card SRS fields directly
- Process reviews via `LearningService.process_card_review()`

## Router Registration

- Each feature has own router
- Register in `bot/telegram/bot.py`
- Error router MUST be last
- Order matters (specific → general)
