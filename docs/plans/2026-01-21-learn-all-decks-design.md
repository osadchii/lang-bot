# Design: Learn All Active Decks

**Date:** 2026-01-21
**Status:** Draft
**Author:** System Architect

## Overview

Two related features to improve the learning experience:

1. **Learn All Active Decks** - Study cards from all active decks at once, prioritized by SRS algorithm
2. **Deck Enable/Disable** - Toggle individual decks' participation in "Learn All" mode

## Requirements Summary

| Requirement | Decision |
|-------------|----------|
| Card selection for "Learn All" | By SRS priority (`next_review`, most overdue first) |
| Toggle UI location | Button in deck details (alongside other actions) |
| "Learn All" button placement | First in deck list, above individual decks |
| Show "Learn All" button | Only if at least one active deck exists |
| Disabled decks in lists | Shown with "(disabled)" label, sorted below active |
| Manual learning of disabled decks | Allowed (user can select any deck manually) |

---

## Layer-by-Layer Changes

### 1. Models Layer

#### File: `bot/database/models/deck.py`

**Add new field:**

```python
class Deck(Base, TimestampMixin):
    # ... existing fields ...

    # New field for deck status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        server_default="true",
    )
```

**Changes:**
- Import `Boolean` from `sqlalchemy`
- Add `is_active` field with default `True`

---

### 2. Repository Layer

#### File: `bot/database/repositories/deck_repo.py`

**Add new methods:**

```python
async def get_user_active_decks(self, user_id: int) -> list[Deck]:
    """Get all active decks for a user.

    Args:
        user_id: User ID

    Returns:
        List of active deck instances
    """
    query = (
        select(Deck)
        .where(Deck.user_id == user_id, Deck.is_active == True)
    )
    result = await self.session.execute(query)
    return list(result.scalars().all())


async def get_user_decks_sorted(self, user_id: int) -> list[Deck]:
    """Get all decks for a user, sorted by is_active (active first).

    Args:
        user_id: User ID

    Returns:
        List of deck instances, active first
    """
    query = (
        select(Deck)
        .where(Deck.user_id == user_id)
        .order_by(Deck.is_active.desc(), Deck.name)
    )
    result = await self.session.execute(query)
    return list(result.scalars().all())


async def count_active_decks(self, user_id: int) -> int:
    """Count active decks for a user.

    Args:
        user_id: User ID

    Returns:
        Number of active decks
    """
    query = (
        select(func.count())
        .select_from(Deck)
        .where(Deck.user_id == user_id, Deck.is_active == True)
    )
    result = await self.session.execute(query)
    return result.scalar_one()
```

#### File: `bot/database/repositories/card_repo.py`

**Add new methods:**

```python
async def get_due_cards_from_decks(
    self,
    deck_ids: list[int],
    limit: int | None = None,
    current_time: datetime | None = None,
) -> list[Card]:
    """Get cards due for review from multiple decks.

    Args:
        deck_ids: List of deck IDs
        limit: Maximum number of cards to return
        current_time: Current time (defaults to now)

    Returns:
        List of due cards, ordered by next_review (oldest first)
    """
    if not deck_ids:
        return []

    if current_time is None:
        current_time = datetime.now(UTC)

    query = (
        select(Card)
        .where(
            Card.deck_id.in_(deck_ids),
            Card.next_review <= current_time,
            Card.repetitions > 0,
        )
        .order_by(Card.next_review.asc())
    )

    if limit is not None:
        query = query.limit(limit)

    result = await self.session.execute(query)
    return list(result.scalars().all())


async def get_new_cards_from_decks(
    self,
    deck_ids: list[int],
    limit: int | None = None,
) -> list[Card]:
    """Get new cards (never reviewed) from multiple decks.

    Args:
        deck_ids: List of deck IDs
        limit: Maximum number of cards to return

    Returns:
        List of new cards
    """
    if not deck_ids:
        return []

    query = (
        select(Card)
        .where(
            Card.deck_id.in_(deck_ids),
            Card.repetitions == 0,
        )
        .order_by(Card.created_at.asc())
    )

    if limit is not None:
        query = query.limit(limit)

    result = await self.session.execute(query)
    return list(result.scalars().all())


async def count_due_cards_from_decks(
    self,
    deck_ids: list[int],
    current_time: datetime | None = None,
) -> int:
    """Count cards due for review from multiple decks.

    Args:
        deck_ids: List of deck IDs
        current_time: Current time (defaults to now)

    Returns:
        Number of due cards
    """
    if not deck_ids:
        return 0

    if current_time is None:
        current_time = datetime.now(UTC)

    query = (
        select(func.count())
        .select_from(Card)
        .where(
            Card.deck_id.in_(deck_ids),
            Card.next_review <= current_time,
            Card.repetitions > 0,
        )
    )
    result = await self.session.execute(query)
    return result.scalar_one()


async def count_new_cards_from_decks(self, deck_ids: list[int]) -> int:
    """Count new cards from multiple decks.

    Args:
        deck_ids: List of deck IDs

    Returns:
        Number of new cards
    """
    if not deck_ids:
        return 0

    query = (
        select(func.count())
        .select_from(Card)
        .where(
            Card.deck_id.in_(deck_ids),
            Card.repetitions == 0,
        )
    )
    result = await self.session.execute(query)
    return result.scalar_one()
```

---

### 3. Services Layer

#### File: `bot/services/deck_service.py`

**Add new methods:**

```python
async def get_user_decks_sorted(self, user_id: int) -> list[Deck]:
    """Get all decks for a user, sorted (active first).

    Args:
        user_id: User ID

    Returns:
        List of deck instances, active first
    """
    return await self.repo.get_user_decks_sorted(user_id)


async def get_active_decks(self, user_id: int) -> list[Deck]:
    """Get active decks for a user.

    Args:
        user_id: User ID

    Returns:
        List of active deck instances
    """
    return await self.repo.get_user_active_decks(user_id)


async def has_active_decks(self, user_id: int) -> bool:
    """Check if user has any active decks.

    Args:
        user_id: User ID

    Returns:
        True if user has at least one active deck
    """
    count = await self.repo.count_active_decks(user_id)
    return count > 0


async def toggle_deck_active(self, deck: Deck) -> Deck:
    """Toggle deck active status.

    Args:
        deck: Deck instance to toggle

    Returns:
        Updated deck instance
    """
    return await self.repo.update(deck, is_active=not deck.is_active)


async def set_deck_active(self, deck: Deck, is_active: bool) -> Deck:
    """Set deck active status.

    Args:
        deck: Deck instance to update
        is_active: New active status

    Returns:
        Updated deck instance
    """
    return await self.repo.update(deck, is_active=is_active)
```

#### File: `bot/services/learning_service.py`

**Add new method:**

```python
async def get_all_decks_learning_session(
    self,
    deck_ids: list[int],
    max_cards: int = DEFAULT_CARDS_PER_SESSION,
    max_new_cards: int = MAX_NEW_CARDS_PER_DAY,
) -> list[Card]:
    """Get cards for a learning session from multiple decks.

    Cards are selected by SRS priority (most overdue first).

    Args:
        deck_ids: List of deck IDs to include
        max_cards: Maximum total cards
        max_new_cards: Maximum new cards to include

    Returns:
        List of cards for the session
    """
    if not deck_ids:
        return []

    # Get new and due cards from all specified decks
    new_cards = await self.card_repo.get_new_cards_from_decks(
        deck_ids, limit=max_new_cards
    )
    due_cards = await self.card_repo.get_due_cards_from_decks(
        deck_ids, limit=max_cards
    )

    # Prioritize due cards
    due_cards = prioritize_cards(due_cards)

    # Mix new and review cards
    session_cards = mix_new_and_review_cards(
        new_cards=new_cards,
        review_cards=due_cards,
        new_cards_limit=max_new_cards,
        total_limit=max_cards,
    )

    return session_cards


async def get_all_decks_stats(self, deck_ids: list[int]) -> dict:
    """Get combined statistics for multiple decks.

    Args:
        deck_ids: List of deck IDs

    Returns:
        Dictionary with combined statistics
    """
    if not deck_ids:
        return {
            "total_cards": 0,
            "new_cards": 0,
            "due_cards": 0,
        }

    new_count, due_count = await asyncio.gather(
        self.card_repo.count_new_cards_from_decks(deck_ids),
        self.card_repo.count_due_cards_from_decks(deck_ids),
    )

    return {
        "total_cards": new_count + due_count,
        "new_cards": new_count,
        "due_cards": due_count,
    }
```

---

### 4. Messages Layer

#### File: `bot/messages/decks.py`

**Add new messages:**

```python
# Deck status labels
LABEL_DECK_DISABLED = "(disabled)"

# Deck toggle messages
MSG_DECK_ENABLED = "Deck <b>{name}</b> enabled.\nIt will be included in 'Learn All'."
MSG_DECK_DISABLED = "Deck <b>{name}</b> disabled.\nIt will not be included in 'Learn All'."

# Button labels
BTN_ENABLE_DECK = "Enable deck"
BTN_DISABLE_DECK = "Disable deck"


def get_deck_display_name(name: str, is_active: bool) -> str:
    """Get deck display name with status label if disabled.

    Args:
        name: Deck name
        is_active: Whether deck is active

    Returns:
        Display name with optional label
    """
    if is_active:
        return html.escape(name)
    return f"{html.escape(name)} {LABEL_DECK_DISABLED}"


def get_deck_toggle_message(name: str, is_now_active: bool) -> str:
    """Get message for deck toggle action.

    Args:
        name: Deck name
        is_now_active: New active status

    Returns:
        Toggle confirmation message
    """
    if is_now_active:
        return MSG_DECK_ENABLED.format(name=html.escape(name))
    return MSG_DECK_DISABLED.format(name=html.escape(name))
```

#### File: `bot/messages/learning.py`

**Add new messages:**

```python
# Learn all button and messages
BTN_LEARN_ALL = "Learn All Decks"
MSG_SELECT_DECK_OR_ALL = (
    "<b>Start Learning</b>\n\n"
    "Choose a deck or learn from all active decks:"
)
MSG_NO_ACTIVE_DECKS_FOR_LEARN_ALL = (
    "No cards to review in active decks.\n"
    "All your cards are up to date, or all decks are disabled."
)
MSG_ALL_DECKS_SESSION_COMPLETE = (
    "<b>Session Complete!</b>\n\n"
    "<b>Cards reviewed:</b> {cards_reviewed}\n"
    "<b>Correct answers:</b> {correct_count}\n"
    "<b>Accuracy:</b> {accuracy:.1f}%\n\n"
    "Cards from multiple decks were included."
)
```

---

### 5. Keyboards Layer

#### File: `bot/telegram/keyboards/deck_keyboards.py`

**Modify existing + add new functions:**

```python
def get_deck_list_keyboard(
    decks: list[Deck],
    show_learn_all: bool = False,
) -> InlineKeyboardMarkup:
    """Get keyboard with list of decks.

    Args:
        decks: List of deck instances (should be sorted: active first)
        show_learn_all: Whether to show "Learn All" button

    Returns:
        Inline keyboard with deck buttons
    """
    builder = InlineKeyboardBuilder()

    # "Learn All" button first if enabled
    if show_learn_all:
        builder.button(text=learn_msg.BTN_LEARN_ALL, callback_data="learn:all")

    for deck in decks:
        display_name = deck_msg.get_deck_display_name(deck.name, deck.is_active)
        builder.button(text=display_name, callback_data=f"deck:{deck.id}")

    builder.button(text=deck_msg.BTN_CREATE_DECK, callback_data="deck:create")
    builder.button(text=common_msg.BTN_BACK_TO_MENU, callback_data="main_menu")

    builder.adjust(1)

    return builder.as_markup()


def get_learning_deck_list_keyboard(
    decks: list[Deck],
    show_learn_all: bool = False,
) -> InlineKeyboardMarkup:
    """Get keyboard with list of decks for learning.

    Args:
        decks: List of deck instances (should be sorted: active first)
        show_learn_all: Whether to show "Learn All" button

    Returns:
        Inline keyboard with deck buttons for learning
    """
    builder = InlineKeyboardBuilder()

    # "Learn All" button first if enabled
    if show_learn_all:
        builder.button(text=learn_msg.BTN_LEARN_ALL, callback_data="learn:all")

    for deck in decks:
        display_name = deck_msg.get_deck_display_name(deck.name, deck.is_active)
        builder.button(text=display_name, callback_data=f"learn:{deck.id}")

    builder.button(text=common_msg.BTN_BACK_TO_MENU, callback_data="main_menu")

    builder.adjust(1)

    return builder.as_markup()


def get_deck_actions_keyboard(deck_id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Get keyboard with deck actions.

    Args:
        deck_id: Deck ID
        is_active: Whether deck is currently active

    Returns:
        Inline keyboard with deck action buttons
    """
    builder = InlineKeyboardBuilder()

    builder.button(text=deck_msg.BTN_START_LEARNING, callback_data=f"learn:{deck_id}")
    builder.button(text=deck_msg.BTN_ADD_CARD_TO_DECK, callback_data=f"add_card:{deck_id}")
    builder.button(text=deck_msg.BTN_VIEW_CARDS, callback_data=f"view_cards:{deck_id}")
    builder.button(text=deck_msg.BTN_EDIT_DECK, callback_data=f"edit_deck:{deck_id}")

    # Toggle button based on current status
    if is_active:
        builder.button(
            text=deck_msg.BTN_DISABLE_DECK,
            callback_data=f"toggle_deck:{deck_id}",
        )
    else:
        builder.button(
            text=deck_msg.BTN_ENABLE_DECK,
            callback_data=f"toggle_deck:{deck_id}",
        )

    builder.button(text=deck_msg.BTN_DELETE_DECK, callback_data=f"delete_deck:{deck_id}")
    builder.button(text=common_msg.BTN_BACK_TO_DECKS, callback_data="decks")

    builder.adjust(1)

    return builder.as_markup()
```

#### File: `bot/telegram/keyboards/learning_keyboards.py`

**No changes needed** - existing keyboards work for both single deck and all-decks sessions.

---

### 6. Handlers Layer

#### File: `bot/telegram/handlers/deck_management.py`

**Modify existing handlers:**

1. **`show_decks`** - Use sorted decks list
2. **`show_deck_details`** - Pass `is_active` to keyboard

**Add new handler:**

```python
@router.callback_query(F.data.startswith("toggle_deck:"))
async def toggle_deck_status(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
):
    """Toggle deck active status.

    Args:
        callback: Callback query
        session: Database session
        user: User instance
    """
    deck_id = parse_callback_int(callback.data)
    if deck_id is None:
        await callback.answer(common_msg.MSG_INVALID_DATA)
        return

    deck_service = DeckService(session)
    deck = await deck_service.get_deck(deck_id)

    if not deck:
        await callback.answer(common_msg.MSG_INVALID_DATA, show_alert=True)
        return

    if deck.user_id != user.id:
        await callback.answer(common_msg.MSG_INVALID_DATA, show_alert=True)
        return

    # Toggle status
    deck = await deck_service.toggle_deck_active(deck)

    # Show confirmation
    await callback.answer(
        deck_msg.get_deck_toggle_message(deck.name, deck.is_active),
        show_alert=True,
    )

    # Refresh deck details view
    deck, card_count = await deck_service.get_deck_with_stats(deck_id)
    text = deck_msg.get_deck_details_message(deck.name, deck.description, card_count)
    await callback.message.edit_text(
        text,
        reply_markup=get_deck_actions_keyboard(deck_id, deck.is_active),
    )
```

#### File: `bot/telegram/handlers/learning.py`

**Modify existing handlers:**

1. **`start_learning_deck_selection`** - Use sorted decks + show "Learn All" if has active decks

**Add new handler:**

```python
@router.callback_query(F.data == "learn:all")
async def start_learn_all_session(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    """Start a learning session for all active decks.

    Args:
        callback: Callback query
        session: Database session
        state: FSM state
        user: User instance
    """
    deck_service = DeckService(session)
    learning_service = LearningService(session)

    # Get active deck IDs
    active_decks = await deck_service.get_active_decks(user.id)
    deck_ids = [deck.id for deck in active_decks]

    if not deck_ids:
        await callback.message.edit_text(learn_msg.MSG_NO_ACTIVE_DECKS_FOR_LEARN_ALL)
        await callback.answer()
        return

    # Get learning session cards from all active decks
    session_cards = await learning_service.get_all_decks_learning_session(
        deck_ids, max_cards=20
    )

    if not session_cards:
        await callback.message.edit_text(learn_msg.MSG_ALL_CARDS_REVIEWED)
        await callback.answer()
        return

    # Store session data in state
    card_ids = [card.id for card in session_cards]
    await state.update_data(
        deck_id=None,  # None indicates "all decks" mode
        deck_ids=deck_ids,  # Store which decks were included
        card_ids=card_ids,
        current_index=0,
        cards_reviewed=0,
        correct_count=0,
        is_all_decks_mode=True,
    )

    # Show first card
    await show_card_front(callback, state, session)
```

**Modify `start_learning_session`:**

```python
@router.callback_query(F.data.startswith("learn:") & ~F.data.in_(["learn:all"]))
async def start_learning_session(
    # ... existing signature ...
):
    # Add is_all_decks_mode=False to state data
    await state.update_data(
        deck_id=deck_id,
        card_ids=card_ids,
        current_index=0,
        cards_reviewed=0,
        correct_count=0,
        is_all_decks_mode=False,
    )
    # ... rest unchanged ...
```

**Modify `continue_learning`:**

```python
@router.callback_query(F.data == "continue_learning")
async def continue_learning(callback: CallbackQuery, session: AsyncSession, user: User):
    """Continue learning with deck selection.

    Args:
        callback: Callback query
        session: Database session
        user: User instance
    """
    deck_service = DeckService(session)
    decks = await deck_service.get_user_decks_sorted(user.id)
    has_active = await deck_service.has_active_decks(user.id)

    keyboard = get_learning_deck_list_keyboard(decks, show_learn_all=has_active)
    await callback.message.edit_text(learn_msg.MSG_CONTINUE_LEARNING, reply_markup=keyboard)
    await callback.answer()
```

---

### 7. Database Migration

#### File: `migrations/versions/YYYYMMDD_add_deck_is_active.py`

```python
"""Add is_active field to decks table.

Revision ID: YYYYMMDDXXXXXX
Revises: 20260121000000
Create Date: 2026-01-21

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'YYYYMMDDXXXXXX'
down_revision = '20260121000000_add_conversation_messages'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'decks',
        sa.Column(
            'is_active',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
    )


def downgrade() -> None:
    op.drop_column('decks', 'is_active')
```

---

## Implementation Order

### Phase 1: Database Layer (Foundation)
1. Add `is_active` field to `Deck` model
2. Create and test migration
3. Add new repository methods

### Phase 2: Service Layer (Business Logic)
4. Add `DeckService` methods for active deck handling
5. Add `LearningService.get_all_decks_learning_session()`

### Phase 3: Messages (UI Text)
6. Add new messages in `bot/messages/decks.py`
7. Add new messages in `bot/messages/learning.py`

### Phase 4: Keyboards (UI Structure)
8. Modify `get_deck_list_keyboard()` to accept `show_learn_all`
9. Add `get_learning_deck_list_keyboard()`
10. Modify `get_deck_actions_keyboard()` to accept `is_active`

### Phase 5: Handlers (Integration)
11. Add `toggle_deck_status` handler
12. Modify `show_decks` to use sorted decks
13. Modify `show_deck_details` to pass `is_active`
14. Add `start_learn_all_session` handler
15. Modify `start_learning_deck_selection` to show "Learn All"
16. Modify `continue_learning` to show "Learn All"

### Phase 6: Testing
17. Write unit tests for repository methods
18. Write unit tests for service methods
19. Write integration tests for handlers

---

## Tests to Write/Update

### New Tests

#### `tests/test_repositories/test_deck_repo.py`

```python
class TestDeckRepository:
    async def test_get_user_active_decks(self):
        """Test getting only active decks."""

    async def test_get_user_decks_sorted(self):
        """Test decks are sorted active-first."""

    async def test_count_active_decks(self):
        """Test counting active decks only."""
```

#### `tests/test_repositories/test_card_repo.py`

```python
class TestCardRepository:
    async def test_get_due_cards_from_decks(self):
        """Test getting due cards from multiple decks."""

    async def test_get_due_cards_from_decks_empty_list(self):
        """Test with empty deck list returns empty."""

    async def test_get_new_cards_from_decks(self):
        """Test getting new cards from multiple decks."""

    async def test_count_due_cards_from_decks(self):
        """Test counting due cards from multiple decks."""

    async def test_count_new_cards_from_decks(self):
        """Test counting new cards from multiple decks."""
```

#### `tests/test_services/test_deck_service.py`

```python
class TestDeckService:
    async def test_get_user_decks_sorted(self):
        """Test decks returned sorted by active status."""

    async def test_get_active_decks(self):
        """Test only active decks returned."""

    async def test_has_active_decks_true(self):
        """Test returns True when active decks exist."""

    async def test_has_active_decks_false(self):
        """Test returns False when no active decks."""

    async def test_toggle_deck_active(self):
        """Test toggling deck active status."""

    async def test_set_deck_active(self):
        """Test setting deck active status explicitly."""
```

#### `tests/test_services/test_learning_service.py`

```python
class TestLearningService:
    async def test_get_all_decks_learning_session(self):
        """Test getting cards from multiple decks."""

    async def test_get_all_decks_learning_session_prioritizes_overdue(self):
        """Test most overdue cards come first."""

    async def test_get_all_decks_learning_session_empty_decks(self):
        """Test with no deck IDs returns empty."""

    async def test_get_all_decks_stats(self):
        """Test combined statistics from multiple decks."""
```

### Update Existing Tests

#### `tests/conftest.py`

Add fixtures:

```python
@pytest_asyncio.fixture
async def sample_user(db_session, sample_user_data):
    """Create sample user in database."""
    from bot.database.repositories.user_repo import UserRepository
    repo = UserRepository(db_session)
    return await repo.create(**sample_user_data)


@pytest_asyncio.fixture
async def sample_deck(db_session, sample_user, sample_deck_data):
    """Create sample deck in database."""
    from bot.database.repositories.deck_repo import DeckRepository
    repo = DeckRepository(db_session)
    return await repo.create(user_id=sample_user.id, **sample_deck_data)


@pytest_asyncio.fixture
async def sample_inactive_deck(db_session, sample_user):
    """Create sample inactive deck in database."""
    from bot.database.repositories.deck_repo import DeckRepository
    repo = DeckRepository(db_session)
    return await repo.create(
        user_id=sample_user.id,
        name="Inactive Deck",
        is_active=False,
    )
```

---

## Callback Data Format

| Action | Format | Example |
|--------|--------|---------|
| Learn all decks | `learn:all` | `learn:all` |
| Learn specific deck | `learn:{deck_id}` | `learn:123` |
| Toggle deck status | `toggle_deck:{deck_id}` | `toggle_deck:123` |
| View deck | `deck:{deck_id}` | `deck:123` |

---

## State Data Structure

### Single Deck Session
```python
{
    "deck_id": 123,
    "card_ids": [1, 2, 3, ...],
    "current_index": 0,
    "cards_reviewed": 0,
    "correct_count": 0,
    "is_all_decks_mode": False,
}
```

### All Decks Session
```python
{
    "deck_id": None,
    "deck_ids": [1, 2, 3],  # Active deck IDs
    "card_ids": [10, 20, 30, ...],
    "current_index": 0,
    "cards_reviewed": 0,
    "correct_count": 0,
    "is_all_decks_mode": True,
}
```

---

## UI Flow Diagrams

### Learn All Flow

```
[Main Menu]
     |
     v
[BTN: "Learn"]
     |
     v
+---------------------------+
| Select Deck               |
+---------------------------+
| [Learn All Decks]   <---- First, only if has active
| [Deck 1]                  |
| [Deck 2]                  |
| [Deck 3 (disabled)]       |
| [Back to Menu]            |
+---------------------------+
     |
     v (select "Learn All Decks")
     |
     v
[Learning Session with mixed cards from all active decks]
```

### Deck Toggle Flow

```
[Deck List]
     |
     v (select deck)
     |
+---------------------------+
| Deck: "My Greek Words"    |
| Cards: 150                |
+---------------------------+
| [Start Learning]          |
| [Add Card]                |
| [View Cards]              |
| [Edit Deck]               |
| [Disable Deck]      <---- Toggle button
| [Delete Deck]             |
| [Back to Decks]           |
+---------------------------+
     |
     v (click "Disable Deck")
     |
+---------------------------+
| Deck: "My Greek Words"    |
| Cards: 150                |
+---------------------------+
| [Start Learning]          |
| [Add Card]                |
| [View Cards]              |
| [Edit Deck]               |
| [Enable Deck]       <---- Now shows Enable
| [Delete Deck]             |
| [Back to Decks]           |
+---------------------------+
```

---

## Edge Cases

1. **All decks disabled**: Show deck list without "Learn All" button
2. **No cards in active decks**: Show "No cards to review" message
3. **Single active deck**: "Learn All" works same as selecting that deck
4. **Toggle during session**: Does not affect current session
5. **Deleted card during session**: Skip card, continue with next

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Migration fails on production | High | Test migration on staging first; prepare rollback script |
| Performance with many decks | Medium | Use efficient SQL with `IN` clause; limit card fetch |
| State inconsistency | Medium | Store `is_all_decks_mode` flag explicitly |
| UI confusion | Low | Clear labeling; "(disabled)" suffix on deck names |

---

## Future Considerations

1. **Quick toggle from deck list**: Add inline enable/disable without entering deck details
2. **Deck groups**: Allow grouping decks for batch enable/disable
3. **Schedule-based activation**: Auto-enable decks at certain times
4. **Statistics per mode**: Track "Learn All" vs single deck performance separately
