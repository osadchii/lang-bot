# Critical Constraints

## NON-NEGOTIABLE RULES

### Architecture
- NEVER skip layers: Handlers → Services → Repositories → Models
- NEVER access Repositories or Models from Handlers
- NEVER put business logic in Handlers

### Database
- NEVER create sessions manually in handlers (use injected session)
- NEVER modify SRS fields directly (use `calculate_next_review()`)
- NEVER skip migrations for model changes

### Async
- ALWAYS use async/await for I/O operations
- NEVER use sync database drivers (only asyncpg)
- NEVER use blocking calls without await

### State Management
- ALWAYS clear FSM state on completion or cancellation
- NEVER leave state dangling

### Configuration
- ALWAYS use Pydantic Settings (bot/config/settings.py)
- NEVER hardcode credentials or tokens
- NEVER use os.getenv() directly

### Code Organization
- NEVER put business logic outside Services layer
- NEVER mix Telegram-specific code in Services
- NEVER create circular imports (import handlers in functions)

### Error Handling
- NEVER swallow errors silently (except: pass)
- NEVER show technical errors to users
- ALWAYS log errors before re-raising

### Code Style
- NEVER use emojis in codebase
- ALWAYS follow Black formatting (line length: 100)
- ALWAYS use type hints
- NEVER commit commented-out code
- NEVER commit unused imports/variables
