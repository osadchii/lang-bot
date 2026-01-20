# Database Schema Documentation

## Overview

The database uses **PostgreSQL** with **SQLAlchemy 2.0** async ORM. All models inherit from `Base` and use Alembic for migrations.

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │
│─────────────────│
│ id (PK)         │
│ telegram_id     │◄─────┐
│ username        │      │
│ first_name      │      │
│ language_code   │      │
│ created_at      │      │
│ updated_at      │      │
└─────────────────┘      │
         │               │
         │ 1             │
         │               │
         ▼ N             │
┌─────────────────┐      │
│      Deck       │      │
│─────────────────│      │
│ id (PK)         │      │
│ user_id (FK)────┼──────┘
│ name            │
│ description     │
│ created_at      │
│ updated_at      │
└─────────────────┘
         │
         │ 1
         │
         ▼ N
┌─────────────────────────────┐
│           Card              │
│─────────────────────────────│
│ id (PK)                     │
│ deck_id (FK)                │
│ front                       │
│ back                        │
│ example                     │
│ notes                       │
│ ease_factor                 │
│ interval                    │
│ repetitions                 │
│ next_review                 │
│ total_reviews               │
│ correct_reviews             │
│ created_at                  │
│ updated_at                  │
└─────────────────────────────┘
         │
         │ 1
         │
         ▼ N
┌─────────────────────────────┐
│          Review             │
│─────────────────────────────│
│ id (PK)                     │
│ card_id (FK)                │
│ user_id (FK)                │
│ quality                     │
│ reviewed_at                 │
│ time_spent                  │
│ ease_factor_before          │
│ interval_before             │
└─────────────────────────────┘

         User
         │
         │ 1
         │
         ▼ N
┌─────────────────────────────┐
│      LearningStats          │
│─────────────────────────────│
│ id (PK)                     │
│ user_id (FK)                │
│ deck_id (FK)                │
│ date                        │
│ cards_reviewed              │
│ cards_learned               │
│ correct_answers             │
│ total_answers               │
│ time_spent                  │
│ streak_days                 │
│ created_at                  │
│ updated_at                  │
└─────────────────────────────┘
```

## Table Definitions

### User

Stores Telegram user information.

| Column         | Type      | Constraints | Description                    |
|----------------|-----------|-------------|--------------------------------|
| id             | Integer   | PK          | Auto-increment primary key     |
| telegram_id    | BigInt    | UNIQUE, NOT NULL | Telegram user ID        |
| username       | String    | NULL        | Telegram username              |
| first_name     | String    | NULL        | User's first name              |
| language_code  | String    | NULL        | User's language preference     |
| created_at     | DateTime  | NOT NULL    | Account creation timestamp     |
| updated_at     | DateTime  | NOT NULL    | Last update timestamp          |

**Indexes**:
- Primary key on `id`
- Unique index on `telegram_id`

**Relationships**:
- `decks`: One-to-Many with Deck
- `reviews`: One-to-Many with Review
- `learning_stats`: One-to-Many with LearningStats

**Constraints**:
- None additional

---

### Deck

Organizes flashcards into collections.

| Column       | Type     | Constraints | Description                   |
|--------------|----------|-------------|-------------------------------|
| id           | Integer  | PK          | Auto-increment primary key    |
| user_id      | Integer  | FK, NOT NULL | Reference to User            |
| name         | String   | NOT NULL    | Deck name (max 255 chars)     |
| description  | Text     | NULL        | Optional deck description     |
| created_at   | DateTime | NOT NULL    | Creation timestamp            |
| updated_at   | DateTime | NOT NULL    | Last update timestamp         |

**Indexes**:
- Primary key on `id`
- Foreign key on `user_id`

**Relationships**:
- `user`: Many-to-One with User
- `cards`: One-to-Many with Card (CASCADE DELETE)
- `learning_stats`: One-to-Many with LearningStats (CASCADE DELETE)

**Constraints**:
- `UNIQUE(user_id, name)`: Each user can't have duplicate deck names

**File**: `bot/database/models/deck.py`

---

### Card

Flashcards with spaced repetition data.

| Column          | Type     | Constraints | Description                        |
|-----------------|----------|-------------|------------------------------------|
| id              | Integer  | PK          | Auto-increment primary key         |
| deck_id         | Integer  | FK, NOT NULL | Reference to Deck                 |
| front           | Text     | NOT NULL    | Front of card (Greek)              |
| back            | Text     | NOT NULL    | Back of card (Translation)         |
| example         | Text     | NULL        | Example sentence                   |
| notes           | Text     | NULL        | Additional notes                   |
| ease_factor     | Float    | NOT NULL    | SRS ease factor (default 2.5)      |
| interval        | Integer  | NOT NULL    | Days until next review (default 0) |
| repetitions     | Integer  | NOT NULL    | Consecutive correct reviews (default 0) |
| next_review     | DateTime | NOT NULL    | When card is due                   |
| total_reviews   | Integer  | NOT NULL    | Total number of reviews (default 0)|
| correct_reviews | Integer  | NOT NULL    | Correct reviews count (default 0)  |
| created_at      | DateTime | NOT NULL    | Creation timestamp                 |
| updated_at      | DateTime | NOT NULL    | Last update timestamp              |

**Indexes**:
- Primary key on `id`
- Foreign key on `deck_id`
- Index on `next_review`
- **Composite index on `(deck_id, next_review)`** - For fetching due cards
- **Composite index on `(deck_id, repetitions)`** - For fetching new cards

**Relationships**:
- `deck`: Many-to-One with Deck
- `reviews`: One-to-Many with Review (CASCADE DELETE)

**Properties**:
- `success_rate`: Calculated property (correct_reviews / total_reviews * 100)
- `is_due`: Calculated property (next_review <= now)

**File**: `bot/database/models/card.py`

---

### Review

History of all card reviews for analytics.

| Column             | Type     | Constraints | Description                      |
|--------------------|----------|-------------|----------------------------------|
| id                 | Integer  | PK          | Auto-increment primary key       |
| card_id            | Integer  | FK, NOT NULL | Reference to Card               |
| user_id            | Integer  | FK, NOT NULL | Reference to User               |
| quality            | Integer  | NOT NULL, CHECK | Quality rating (0, 2, 3, 5) |
| reviewed_at        | DateTime | NOT NULL    | When review occurred             |
| time_spent         | Integer  | NULL        | Time spent in seconds            |
| ease_factor_before | Float    | NULL        | Ease factor before review        |
| interval_before    | Integer  | NULL        | Interval before review           |

**Indexes**:
- Primary key on `id`
- Foreign key on `card_id`
- Foreign key on `user_id`
- Index on `reviewed_at`
- **Composite index on `(user_id, reviewed_at)`** - For user review history

**Relationships**:
- `card`: Many-to-One with Card
- `user`: Many-to-One with User

**Constraints**:
- `CHECK(quality IN (0, 2, 3, 5))`: Only valid quality values allowed

**File**: `bot/database/models/review.py`

---

### LearningStats

Daily statistics per user per deck.

| Column          | Type     | Constraints | Description                     |
|-----------------|----------|-------------|---------------------------------|
| id              | Integer  | PK          | Auto-increment primary key      |
| user_id         | Integer  | FK, NOT NULL | Reference to User              |
| deck_id         | Integer  | FK, NOT NULL | Reference to Deck              |
| date            | Date     | NOT NULL    | Statistics date                 |
| cards_reviewed  | Integer  | NOT NULL    | Cards reviewed today (default 0)|
| cards_learned   | Integer  | NOT NULL    | New cards learned (default 0)   |
| correct_answers | Integer  | NOT NULL    | Correct answers (default 0)     |
| total_answers   | Integer  | NOT NULL    | Total answers (default 0)       |
| time_spent      | Integer  | NOT NULL    | Time spent in seconds (default 0)|
| streak_days     | Integer  | NOT NULL    | Current streak (default 0)      |
| created_at      | DateTime | NOT NULL    | Creation timestamp              |
| updated_at      | DateTime | NOT NULL    | Last update timestamp           |

**Indexes**:
- Primary key on `id`
- Foreign key on `user_id`
- Foreign key on `deck_id`
- Index on `date`
- **Composite index on `(user_id, deck_id, date)`** - For daily stats queries

**Relationships**:
- `user`: Many-to-One with User
- `deck`: Many-to-One with Deck

**Constraints**:
- `UNIQUE(user_id, deck_id, date)`: One stats record per user/deck/day

**Properties**:
- `accuracy`: Calculated property (correct_answers / total_answers * 100)

**File**: `bot/database/models/learning_stats.py`

## Database Constraints Summary

### Primary Keys
All tables use auto-incrementing integer primary keys.

### Foreign Keys
All foreign keys use `ondelete="CASCADE"`:
- Deleting a user deletes all their decks, reviews, and stats
- Deleting a deck deletes all its cards and stats
- Deleting a card deletes all its reviews

### Unique Constraints
- `users.telegram_id`: Each Telegram user appears once
- `decks(user_id, name)`: No duplicate deck names per user
- `learning_stats(user_id, deck_id, date)`: One stats record per user/deck/day

### Check Constraints
- `reviews.quality IN (0, 2, 3, 5)`: Enforces valid quality ratings

### Indexes

**Single Column Indexes**:
- `users.telegram_id` (unique)
- `cards.next_review`
- `reviews.reviewed_at`
- `learning_stats.date`

**Composite Indexes** (Performance optimization):
- `cards(deck_id, next_review)` - Get due cards efficiently
- `cards(deck_id, repetitions)` - Get new cards efficiently
- `reviews(user_id, reviewed_at)` - User review history
- `learning_stats(user_id, deck_id, date)` - Daily stats lookup

## Migration Management

### Creating Migrations

After modifying models:

```bash
# Auto-generate migration
alembic revision --autogenerate -m "Add new feature"

# Review generated migration
cat migrations/versions/XXXXX_add_new_feature.py

# Apply migration
alembic upgrade head
```

### Current Migrations

1. **Initial migration** (auto-generated):
   - Created all base tables
   - Set up relationships

2. **20260120213939_add_database_constraints_and_composite_indexes**:
   - Added CHECK constraint on reviews.quality
   - Added UNIQUE constraints
   - Added composite indexes for performance

### Migration Best Practices

1. **Always review** auto-generated migrations before applying
2. **Test migrations** on development database first
3. **Include both upgrade and downgrade** paths
4. **Never edit applied migrations** - create new ones instead
5. **Backup production database** before major migrations

## Common Queries

### Get Due Cards for a Deck

```python
from datetime import datetime, timezone
from sqlalchemy import select

stmt = select(Card).where(
    Card.deck_id == deck_id,
    Card.next_review <= datetime.now(timezone.utc)
).order_by(Card.next_review)

cards = await session.execute(stmt)
due_cards = cards.scalars().all()
```

**Optimized by**: Composite index `(deck_id, next_review)`

### Get New Cards

```python
stmt = select(Card).where(
    Card.deck_id == deck_id,
    Card.repetitions == 0
).limit(20)

cards = await session.execute(stmt)
new_cards = cards.scalars().all()
```

**Optimized by**: Composite index `(deck_id, repetitions)`

### Get User's Daily Stats

```python
from datetime import date

stmt = select(LearningStats).where(
    LearningStats.user_id == user_id,
    LearningStats.deck_id == deck_id,
    LearningStats.date == date.today()
)

stats = await session.execute(stmt)
daily_stats = stats.scalar_one_or_none()
```

**Optimized by**: Composite index `(user_id, deck_id, date)` + UNIQUE constraint

### Get User Review History

```python
stmt = select(Review).where(
    Review.user_id == user_id
).order_by(Review.reviewed_at.desc()).limit(100)

reviews = await session.execute(stmt)
history = reviews.scalars().all()
```

**Optimized by**: Composite index `(user_id, reviewed_at)`

## Data Integrity Rules

### Cascade Deletes

- ✅ Delete user → deletes decks, reviews, stats
- ✅ Delete deck → deletes cards, stats
- ✅ Delete card → deletes reviews
- ✅ All handled automatically by database

### Orphan Prevention

- Foreign keys prevent orphaned records
- All relationships use `nullable=False` where appropriate
- Database-level constraints ensure data integrity

### SRS Data Integrity

- ❌ **Never manually update SRS fields** (ease_factor, interval, repetitions, next_review)
- ✅ **Always use** `calculate_next_review()` function
- ✅ **Validate** SRS results before writing to database

## Database Configuration

Located in `bot/config/settings.py`:

```python
database_url: str  # postgresql+asyncpg://user:pass@host:port/db
db_pool_size: int = 10  # Connection pool size
db_max_overflow: int = 20  # Max overflow connections
db_pool_timeout: int = 30  # Pool timeout in seconds
```

### Connection String Format

```
postgresql+asyncpg://username:password@hostname:port/database_name
```

**Important**: Must use `asyncpg` driver for async support.

## Performance Considerations

### Query Performance
- Use composite indexes for common query patterns
- Limit results with `.limit()`
- Use `.count()` instead of `len(await query.all())`

### Connection Pooling
- Pool size: 10 connections (default)
- Max overflow: 20 (total 30 max connections)
- Adjust based on load and database capacity

### Memory Usage
- Avoid loading large result sets at once
- Use pagination for large queries
- Stream results when possible

## Database Backup

Recommended backup strategy:

```bash
# Daily backup
pg_dump -Fc langbot > backup_$(date +%Y%m%d).dump

# Restore
pg_restore -d langbot backup_20260120.dump
```

## Further Reading

- [Repository API](../api/repositories.md) - Data access patterns
- [Service Layer](./service-layer.md) - How services use models
- [Migration Guide](../development/migrations.md) - Detailed migration workflow

---

**Last Updated**: 2026-01-20
**Maintained by**: Documentation Agent
