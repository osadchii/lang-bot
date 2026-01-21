# Testing Rules

## Coverage Requirements

- Core modules (bot/core/): 100%
- Services (bot/services/): 90%+
- Repositories (bot/database/repositories/): 80%+
- Overall: 80%+

## Must Test

- Core business logic (SRS, card scheduling)
- All service methods
- Repository custom queries
- Complex data transformations
- Critical user flows
- API integrations

## Test Structure

- Files: `test_<module>.py`
- Classes: `Test<ClassName>`
- Functions: `test_<what_it_tests>`
- Use pytest-asyncio (asyncio_mode = "auto")

## Fixtures (tests/conftest.py)

- `db_session` - in-memory SQLite
- `sample_user_data`, `sample_deck_data`, `sample_card_data`
- `sample_user`, `sample_deck`, `sample_card` (create in DB)

## Patterns

- AAA: Arrange-Act-Assert
- One assertion per test (when possible)
- Descriptive test names
- Use @pytest.mark.parametrize for similar tests
- Mock external services (OpenAI API)

## Commands

```bash
pytest                              # All tests
pytest --cov=bot --cov-report=html  # With coverage
pytest -m "not slow"                # Skip slow tests
pytest -x                           # Stop on first failure
```

## Pre-commit Checks

```bash
black bot/ tests/
ruff check bot/ tests/
pytest --cov=bot --cov-fail-under=80
```

## CI Requirements

1. Format check (black)
2. Linting (ruff)
3. Type checking (mypy)
4. Tests with coverage
5. Coverage threshold (80%)
