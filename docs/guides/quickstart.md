# Quick Start Guide

Get your Greek Learning Bot running in 5 minutes!

## Prerequisites

- Python 3.13+
- PostgreSQL running
- Telegram Bot Token
- OpenAI API Key

## Quick Setup

### 1. Install Dependencies

```bash
cd /Users/antonosadcij/PycharmProjects/lang-bot
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
nano .env  # or use any text editor
```

Update these values in `.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/langbot
OPENAI_API_KEY=your_openai_key_here
```

### 3. Create Database

```bash
createdb langbot
```

### 4. Initialize Database

```bash
alembic upgrade head
# OR
python scripts/init_db.py
```

### 5. (Optional) Add Test Data

```bash
python scripts/seed_data.py
```

### 6. Run the Bot

```bash
python -m bot
```

## Verify It Works

1. Open Telegram
2. Find your bot (search by username)
3. Send `/start`
4. You should see the welcome message!

## First Steps in the Bot

1. **Create a Deck**: Tap "My Decks" button, then "Create New Deck"
2. **Add Cards**: Tap "Add Card" button, choose a deck, then enter a word
3. **Start Learning**: Tap "Learn" button, select a deck, and review cards
4. **Try Translation**: Simply type any Greek or Russian word - the bot will translate it and offer to add it as a card
5. **Ask Questions**: Type any language question in Russian - the bot understands context and remembers your conversation

**Smart Translation Flow**:
- Type a word like "σπίτι" or "дом"
- Bot translates and checks if you already have this card
- If not, suggests the best deck or offers to create a new one
- One tap to add the card with AI-generated example

## Troubleshooting

**Bot doesn't start?**
- Check `.env` file has correct values
- Verify PostgreSQL is running: `pg_isready`
- Check logs for specific errors

**Database errors?**
- Ensure database exists: `psql -l | grep langbot`
- Run migrations: `alembic upgrade head`

**OpenAI errors?**
- Verify API key is valid
- Check you have credits

## Next Steps

- Read [SETUP.md](SETUP.md) for detailed setup
- Check [README.md](README.md) for features overview
- See [PROJECT_STATUS.md](PROJECT_STATUS.md) for implementation details

Happy learning Greek!
