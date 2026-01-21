# Greek Language Learning Bot - Setup Guide

## Prerequisites

- Python 3.13 or higher
- PostgreSQL 14 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- OpenAI API Key

## Installation Steps

### 1. Clone and Navigate to Project

```bash
cd /Users/antonosadcij/PycharmProjects/lang-bot
```

### 2. Create Virtual Environment

```bash
python3.13 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

#### Using Poetry (Recommended)

```bash
pip install poetry
poetry install
```

#### Using pip

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

```bash
# Create database
createdb langbot

# Or using psql
psql -U postgres
CREATE DATABASE langbot;
\q
```

### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file with your credentials:

```env
TELEGRAM_BOT_TOKEN=your_actual_bot_token_from_botfather
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/langbot
OPENAI_API_KEY=your_actual_openai_api_key
OPENAI_MODEL=gpt-4
DEBUG=False
LOG_LEVEL=INFO
```

### 6. Initialize Database

#### Option A: Using Alembic (Recommended for Production)

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

#### Option B: Using init_db.py (Quick Setup)

```bash
python scripts/init_db.py
```

### 7. (Optional) Seed Test Data

```bash
python scripts/seed_data.py
```

This will create:
- A test user
- A sample deck with 10 Greek vocabulary cards

## Running the Bot

### Development Mode

```bash
# With Poetry
poetry run python -m bot

# Or directly
python -m bot
```

### Production Mode

```bash
# Set production environment
export DEBUG=False
export LOG_LEVEL=INFO

# Run bot
python -m bot
```

## Verification

### 1. Check Bot is Running

You should see output like:

```
2024-01-20 12:00:00 - bot.__main__ - INFO - ==================================================
2024-01-20 12:00:00 - bot.__main__ - INFO - Greek Language Learning Bot
2024-01-20 12:00:00 - bot.__main__ - INFO - ==================================================
2024-01-20 12:00:00 - bot.telegram.bot - INFO - Bot instance created
2024-01-20 12:00:00 - bot.telegram.bot - INFO - Dispatcher created with middlewares
2024-01-20 12:00:00 - bot.telegram.bot - INFO - All handlers registered
2024-01-20 12:00:00 - bot.__main__ - INFO - Starting Greek Learning Bot...
2024-01-20 12:00:00 - bot.__main__ - INFO - Starting polling...
```

### 2. Test in Telegram

1. Open Telegram and find your bot
2. Send `/start` command
3. You should see the welcome message and main menu

### 3. Test Basic Functionality

- **Create Deck**: Use "My Decks" button, then "Create New Deck"
- **Add Card**: Use "Add Card" button, select deck, enter word
- **Learn**: Use "Learn" button, select deck, review cards
- **Smart Translation**: Type any word (Greek or Russian) - bot will translate and offer to add as card
- **AI Questions**: Type any question in Russian about Greek language

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready

# Check database exists
psql -U postgres -l | grep langbot

# Test connection
psql postgresql://username:password@localhost:5432/langbot
```

### Bot Token Issues

- Verify token is correct from @BotFather
- Ensure no extra spaces in `.env` file
- Token should start with a number and contain a colon

### Import Errors

```bash
# Ensure you're in the project root
pwd  # Should show: /Users/antonosadcij/PycharmProjects/lang-bot

# Reinstall dependencies
pip install -r requirements.txt
```

### OpenAI API Issues

- Verify API key is valid
- Check you have credits/billing enabled
- Test with a simple request

## Development Workflow

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Format code
black bot/

# Lint
ruff check bot/
```

### Database Migrations

```bash
# Create new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

### Adding New Features

1. Make changes to code
2. Update models if needed
3. Create migration: `alembic revision --autogenerate -m "Add feature X"`
4. Apply migration: `alembic upgrade head`
5. Test functionality
6. Commit changes

## Project Structure

```
lang-bot/
├── bot/                      # Main application package
│   ├── config/              # Configuration
│   ├── core/                # Business logic (SRS)
│   ├── database/            # Models & repositories
│   ├── services/            # Service layer
│   ├── telegram/            # Bot handlers & UI
│   └── utils/               # Utilities
├── migrations/              # Database migrations
├── scripts/                 # Helper scripts
├── tests/                   # Tests
├── .env                     # Environment variables (create from .env.example)
├── alembic.ini             # Alembic config
├── pyproject.toml          # Poetry config
└── requirements.txt        # Pip requirements
```

## Next Steps

1. **Customize**: Modify the bot to fit your needs
2. **Add More Cards**: Populate decks with vocabulary
3. **Monitor**: Check logs for any issues
4. **Deploy**: Consider deploying to a server for 24/7 operation

## Support

For issues or questions:
- Check logs in console output
- Review configuration in `.env`
- Ensure all dependencies are installed
- Verify database is accessible

## License

MIT License
