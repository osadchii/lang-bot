# Greek Language Learning Telegram Bot

A Telegram bot for learning Greek with AI-powered assistance and spaced repetition system (SRS).

## Features

- **Spaced Repetition System**: Uses the SM-2 algorithm for optimal learning retention
- **AI Assistant**: Powered by OpenAI GPT-4 for translations, grammar explanations, and card generation
- **Deck Management**: Organize your learning materials into customizable decks
- **Learning Statistics**: Track your progress and learning streaks
- **Interactive Learning**: Review cards with immediate feedback and intelligent scheduling

## Tech Stack

- **Bot Framework**: aiogram 3.x
- **Database**: PostgreSQL with SQLAlchemy 2.0 (async) and asyncpg
- **AI Integration**: OpenAI API (GPT-4)
- **Migrations**: Alembic
- **Configuration**: Pydantic Settings

## Installation

### Prerequisites

- Python 3.13+
- PostgreSQL 14+
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
- OpenAI API Key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd lang-bot
```

2. Install dependencies:
```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. Initialize the database:
```bash
# Run migrations
alembic upgrade head

# Optional: seed test data
python scripts/seed_data.py
```

## Usage

### Running the Bot

```bash
# Using Poetry
poetry run python -m bot

# Or directly with Python
python -m bot
```

### Available Commands

- `/start` - Start the bot and register
- `/help` - Show help information
- `/decks` - Manage your decks
- `/learn` - Start a learning session
- `/stats` - View your learning statistics
- `/ai` - Chat with AI assistant

## Project Structure

```
lang-bot/
├── bot/                    # Main package
│   ├── config/            # Configuration
│   ├── core/              # Business logic (SRS algorithm)
│   ├── database/          # Database models and repositories
│   ├── services/          # Business logic services
│   ├── telegram/          # Telegram bot handlers and UI
│   └── utils/             # Utilities
├── migrations/            # Alembic migrations
├── scripts/               # Helper scripts
└── tests/                 # Tests
```

## Development

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
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Spaced Repetition System

The bot uses the **SM-2 (SuperMemo 2)** algorithm for spaced repetition:

- **Again** (0): Reset the card, review soon
- **Hard** (2): Slightly increase interval
- **Good** (3): Normal interval increase
- **Easy** (5): Large interval increase

Cards are automatically scheduled for review based on your performance.

## Architecture

The project follows a layered architecture:

1. **Presentation Layer**: Telegram handlers (aiogram)
2. **Business Logic Layer**: Services and core logic
3. **Data Access Layer**: SQLAlchemy models and repositories
4. **External Services Layer**: OpenAI API integration

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.
