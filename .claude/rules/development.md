# Development Rules

## Code Style

- Black formatting (line length: 100)
- Ruff for linting
- NO emojis in code
- NO commented-out code
- NO unused imports/variables
- Use type hints everywhere
- Modern union syntax: `str | None` not `Optional[str]`

## Import Order

1. Standard library
2. Third-party packages
3. Local application imports

## Async Requirements

- ALWAYS async for I/O operations
- Use `async def`, `await`, `AsyncSession`
- Use `async with` for context managers
- Use asyncio.gather() for parallel operations

## Error Handling

- Handle expected errors explicitly
- Let global handler catch unexpected errors
- NEVER silent error swallowing
- Log errors with context before re-raising
- User-friendly messages only

## HTML Formatting

- Bot uses HTML parse mode
- Escape user content with `html.escape()`
- Supported tags: `<b>`, `<i>`, `<code>`, `<pre>`, `<a>`

## Callback Data

- Format: `"action:id:extra"`
- Parse with `callback.data.split(":")`

## Database

- Use Repositories for data access
- Use eager loading (joinedload/selectinload) for relationships
- Let middleware handle transactions in handlers
- Manual transactions only in scripts/tests

## Logging

- Use `logger = logging.getLogger(__name__)`
- Always log with context
- Use `exc_info=True` for exceptions

## Anti-Patterns (AVOID)

- Business logic in handlers
- Manual session management in handlers
- Direct model access in services
- Forgotten state cleanup
- Direct SRS field modification
- Circular imports at module level
