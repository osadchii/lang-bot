# Design: Exercise Variety Improvements

**Date:** 2026-01-22
**Status:** Implemented
**Author:** System Architect

## Overview

This document addresses two reported issues with the grammar exercises feature:
1. Exercise repetition - same verb/tense combinations appear consecutively
2. Question equals answer - verb given in present tense, asked to write in present tense

## Problem Analysis

### Problem 1: Exercise Repetition

**Current Code** (`bot/services/exercise_service.py`, line 160):
```python
if user_words:
    word_data = random.choice(user_words)
```

**Issue:**
- No tracking of previously used words or word+tense combinations
- With only 1 verb in deck, the same verb is selected every time
- Even with multiple verbs, same word can be selected consecutively
- No tracking of previously selected tenses either

**Scenario:**
- User has 1 verb in deck: "γραφω"
- Every exercise uses "γραφω"
- Random tense selection can repeat: Aorist, Aorist, Present, Aorist

### Problem 2: Question Equals Answer

**Current Code** (`bot/services/exercise_service.py`, lines 287-292):
```python
tenses = [
    ("Ενεστωτας", "настоящее время"),        # Present
    ("Αοριστος", "прошедшее время (аорист)"),  # Aorist
    ("Μελλοντας", "будущее время"),           # Future
]
tense_greek, tense_russian = random.choice(tenses)
```

**Issue:**
- Verbs in user's cards are stored in present tense (1st person singular)
- Present tense (Ενεστωτας) has 33% selection probability
- When present tense is selected for a verb already in present tense:
  - Given: "γραφω" (present tense)
  - Task: "Put in present tense"
  - Answer: "γραφω" (same as given)

---

## Solution Design

### Solution 1: Exercise History Tracking

**Approach:** Track recently used word+variation combinations to ensure variety.

**Key Concept:** A "variation" is the combination of:
- For tenses: word + target_tense
- For conjugations: word + person
- For cases: noun + case

**Data Structure:**
```python
@dataclass
class ExerciseHistory:
    """Tracks recently used exercise variations."""

    # List of (word, variation_key) tuples, most recent first
    recent_combinations: list[tuple[str, str]]

    # Maximum history size to maintain
    max_history_size: int = 10
```

**FSM State Addition:**
```python
await state.update_data(
    exercise_type=exercise_type_str,
    total_count=0,
    correct_count=0,
    ai_words=[],
    user_words=user_words,
    current_task=None,
    exercise_history=[],  # NEW: list of (word, variation_key) tuples
)
```

**Selection Algorithm:**
```python
def select_word_and_variation(
    words: list[dict],
    variations: list[tuple],  # Available tenses/persons/cases
    history: list[tuple[str, str]],
    max_history: int = 10,
) -> tuple[dict, tuple, list[tuple[str, str]]]:
    """Select word and variation avoiding recent combinations.

    Returns:
        (selected_word, selected_variation, updated_history)
    """
    # Build set of recent combinations for O(1) lookup
    recent_set = set(history[-max_history:])

    # Build list of available (word, variation) pairs not in recent history
    available = []
    for word in words:
        word_key = word["word"]
        for variation in variations:
            variation_key = variation[0]  # e.g., tense name, person id
            if (word_key, variation_key) not in recent_set:
                available.append((word, variation))

    # If all combinations are in history, fallback to least recent
    if not available:
        # Use all combinations, history will naturally cycle
        available = [(word, var) for word in words for var in variations]

    # Random selection from available
    selected_word, selected_variation = random.choice(available)

    # Update history
    new_history = history + [(selected_word["word"], selected_variation[0])]
    if len(new_history) > max_history:
        new_history = new_history[-max_history:]

    return selected_word, selected_variation, new_history
```

### Solution 2: Exclude Source Form from Target Options

**Approach:** Do not ask for a form that matches the source form.

**For Tenses:**
- Verbs in cards are in Present tense (1st person singular)
- When generating tense task, exclude "Ενεστωτας" (Present) from options

**For Conjugations:**
- Verbs in cards are in 1st person singular
- When generating conjugation task, exclude "1st_singular" from options

**For Cases:**
- Nouns in cards are in Nominative case
- When generating case task, exclude "Ονομαστικη" (Nominative) from options

**Updated Tenses List:**
```python
async def _generate_tense_task(
    self,
    word: str,
    translation: str,
    is_from_ai: bool,
    source_tense: str = "Ενεστωτας",  # Default: cards store present tense
) -> ExerciseTask:
    """Generate a tense exercise task.

    Args:
        word: Greek verb
        translation: Russian translation
        is_from_ai: Whether word is AI-generated
        source_tense: The tense the word is currently in (to exclude)
    """
    all_tenses = [
        ("Ενεστωτας", "настоящее время"),
        ("Αοριστος", "прошедшее время (аорист)"),
        ("Μελλοντας", "будущее время"),
    ]

    # Exclude the source tense (word is already in this tense)
    available_tenses = [t for t in all_tenses if t[0] != source_tense]

    tense_greek, tense_russian = random.choice(available_tenses)
    # ... rest of the method
```

**Alternative: AI-Powered Transformation**

Instead of excluding, ask AI to provide a different source form:

```python
# Option A: Transform to different source form
async def _generate_tense_task_with_source_transform(
    self,
    word: str,  # e.g., "γραφω" (present)
    translation: str,
    is_from_ai: bool,
) -> ExerciseTask:
    """Generate tense task with source form transformation.

    1. Randomly pick target tense (including present)
    2. Pick a source tense different from target
    3. Ask AI for the source form
    4. Present source form, ask for target form
    """
    all_tenses = [
        ("Ενεστωτας", "настоящее время"),
        ("Αοριστος", "прошедшее время (аорист)"),
        ("Μελλοντας", "будущее время"),
    ]

    # Pick target tense
    target_tense = random.choice(all_tenses)

    # Pick source tense (different from target)
    source_options = [t for t in all_tenses if t != target_tense]
    source_tense = random.choice(source_options)

    # Get source form from AI
    source_form = await self._get_verb_form(word, source_tense[0])
    target_form = await self._get_verb_form(word, target_tense[0])

    return ExerciseTask(
        word=source_form,  # Show source form, not original
        translation=translation,
        task_text=f"Поставь глагол в {target_tense[1]}",
        task_hint=target_tense[0],
        expected_answer=target_form,
        is_from_ai=is_from_ai,
    )
```

**Recommendation:** Use the simpler exclusion approach for the first iteration:
- Present tense verbs: exclude present tense as target
- 1st person singular verbs: exclude 1st person singular as target
- Nominative nouns: exclude nominative as target

### Solution 3: Minimum Words Threshold with AI Supplement

**Problem:** With only 1 verb, all exercises use the same word.

**Approach:** Supplement user words with AI-generated words when below threshold.

**Configuration:**
```python
# Minimum number of unique words for exercise variety
MIN_WORDS_FOR_EXERCISES = 5

# Number of AI words to generate when below threshold
AI_SUPPLEMENT_COUNT = 3
```

**Implementation:**
```python
async def get_words_with_ai_supplement(
    self,
    user_id: int,
    exercise_type: ExerciseType,
    min_words: int = 5,
    supplement_count: int = 3,
) -> tuple[list[dict], list[dict]]:
    """Get words for exercises, supplementing with AI if needed.

    Returns:
        (all_words, ai_words) - Combined list and list of AI-generated words
    """
    # Get user's words
    user_words = await self.get_user_words_for_exercise(
        user_id=user_id,
        exercise_type=exercise_type,
    )

    ai_words = []

    # Supplement with AI if below threshold
    if len(user_words) < min_words:
        needed = min(supplement_count, min_words - len(user_words))
        for _ in range(needed):
            ai_word = await self._generate_word_with_ai(exercise_type)
            # Avoid duplicates
            if ai_word["word"] not in [w["word"] for w in user_words + ai_words]:
                ai_words.append(ai_word)

    return user_words + ai_words, ai_words
```

**Alternative: Warning Message**

Show a message suggesting the user add more words:
```python
if len(user_words) < MIN_WORDS_FOR_EXERCISES:
    warning = (
        f"У тебя только {len(user_words)} глаголов для практики. "
        f"Добавь еще {MIN_WORDS_FOR_EXERCISES - len(user_words)} слов для лучшего разнообразия, "
        f"или продолжай - AI добавит дополнительные слова."
    )
```

---

## Recommended Solution

### Priority 1: Source Form Exclusion (Fixes Question = Answer)

**Files to modify:**
- `bot/services/exercise_service.py`

**Changes:**
1. In `_generate_tense_task`: Exclude "Ενεστωτας" from available tenses
2. In `_generate_conjugation_task`: Exclude "1st_singular" from available persons
3. In `_generate_case_task`: Exclude "Ονομαστικη" from available cases

**Impact:** Low risk, simple change, immediately fixes the "question = answer" issue.

### Priority 2: Exercise History Tracking (Fixes Repetition)

**Files to modify:**
- `bot/services/exercise_service.py`
- `bot/telegram/handlers/exercises.py`

**Changes:**
1. Add history tracking to FSM state
2. Modify `generate_task` to use `select_word_and_variation` algorithm
3. Pass variation selection to task generation methods

**Impact:** Medium complexity, requires FSM state changes.

### Priority 3: AI Word Supplementation (Addresses Limited Words)

**Files to modify:**
- `bot/services/exercise_service.py`
- `bot/telegram/handlers/exercises.py`

**Changes:**
1. Add `get_words_with_ai_supplement` method
2. Call it in `start_exercise_session` instead of `get_user_words_for_exercise`
3. Track AI words separately for potential card addition

**Impact:** Increases AI API usage, but provides better UX with small decks.

---

## Implementation Plan

### Phase 1: Fix Question = Answer Issue

**File:** `bot/services/exercise_service.py`

**Step 1.1:** Modify `_generate_tense_task` to exclude present tense

```python
async def _generate_tense_task(
    self,
    word: str,
    translation: str,
    is_from_ai: bool,
) -> ExerciseTask:
    """Generate a tense exercise task."""
    all_tenses = [
        ("Ενεστωτας", "настоящее время"),
        ("Αοριστος", "прошедшее время (аорист)"),
        ("Μελλοντας", "будущее время"),
    ]

    # User's cards store verbs in present tense (Ενεστωτας)
    # Exclude present to avoid question = answer
    tenses = [t for t in all_tenses if t[0] != "Ενεστωτας"]

    tense_greek, tense_russian = random.choice(tenses)
    # ... rest unchanged
```

**Step 1.2:** Modify `_generate_conjugation_task` to exclude 1st person singular

```python
async def _generate_conjugation_task(
    self,
    word: str,
    translation: str,
    is_from_ai: bool,
) -> ExerciseTask:
    """Generate a conjugation exercise task."""
    all_persons = [
        ("1st_singular", "εγω", "1-е лицо ед.ч. (εγω)"),
        ("2nd_singular", "εσυ", "2-е лицо ед.ч. (εσυ)"),
        ("3rd_singular", "αυτος", "3-е лицо ед.ч. (αυτος/η/ο)"),
        ("1st_plural", "εμεις", "1-е лицо мн.ч. (εμεις)"),
        ("2nd_plural", "εσεις", "2-е лицо мн.ч. (εσεις)"),
        ("3rd_plural", "αυτοι", "3-е лицо мн.ч. (αυτοι/ες/α)"),
    ]

    # User's cards store verbs in 1st person singular
    # Exclude it to avoid question = answer
    persons = [p for p in all_persons if p[0] != "1st_singular"]

    person_id, pronoun, person_russian = random.choice(persons)
    # ... rest unchanged
```

**Step 1.3:** Modify `_generate_case_task` to exclude nominative

```python
async def _generate_case_task(
    self,
    word: str,
    translation: str,
    is_from_ai: bool,
) -> ExerciseTask:
    """Generate a case exercise task."""
    all_cases = [
        ("Ονομαστικη", "именительный падеж (Ονομαστικη)"),
        ("Γενικη", "родительный падеж (Γενικη)"),
        ("Αιτιατικη", "винительный падеж (Αιτιατικη)"),
        ("Κλητικη", "звательный падеж (Κλητικη)"),
    ]

    # User's cards store nouns in nominative case
    # Exclude it to avoid question = answer
    cases = [c for c in all_cases if c[0] != "Ονομαστικη"]

    case_greek, case_russian = random.choice(cases)
    # ... rest unchanged
```

### Phase 2: Add Exercise History Tracking

**Step 2.1:** Add history data structure

**File:** `bot/services/exercise_service.py`

Add at module level:
```python
# Maximum number of recent combinations to track
MAX_EXERCISE_HISTORY = 10
```

**Step 2.2:** Add selection algorithm

**File:** `bot/services/exercise_service.py`

Add new method:
```python
def _select_word_and_variation(
    self,
    words: list[dict],
    variations: list[tuple],
    history: list[tuple[str, str]],
) -> tuple[dict, tuple, list[tuple[str, str]]]:
    """Select word and variation avoiding recent combinations.

    Args:
        words: Available words (dicts with 'word' and 'translation')
        variations: Available variations (tuples with key as first element)
        history: List of (word, variation_key) tuples

    Returns:
        (selected_word, selected_variation, updated_history)
    """
    recent_set = set(history[-MAX_EXERCISE_HISTORY:])

    # Build available combinations
    available = []
    for word in words:
        word_key = word["word"]
        for variation in variations:
            variation_key = variation[0]
            if (word_key, variation_key) not in recent_set:
                available.append((word, variation))

    # Fallback if all in history
    if not available:
        available = [(word, var) for word in words for var in variations]

    selected_word, selected_variation = random.choice(available)

    # Update history
    new_history = history + [(selected_word["word"], selected_variation[0])]
    if len(new_history) > MAX_EXERCISE_HISTORY:
        new_history = new_history[-MAX_EXERCISE_HISTORY:]

    return selected_word, selected_variation, new_history
```

**Step 2.3:** Refactor generate_task to accept history

```python
async def generate_task(
    self,
    exercise_type: ExerciseType,
    user_words: list[dict] | None = None,
    history: list[tuple[str, str]] | None = None,
) -> tuple[ExerciseTask, list[tuple[str, str]]]:
    """Generate an exercise task with history tracking.

    Args:
        exercise_type: Type of exercise
        user_words: Optional list of user's words
        history: Optional list of recent (word, variation) combinations

    Returns:
        (ExerciseTask, updated_history)
    """
    history = history or []

    # Define variations based on exercise type
    if exercise_type == ExerciseType.TENSES:
        variations = [
            ("Αοριστος", "прошедшее время (аорист)"),
            ("Μελλοντας", "будущее время"),
        ]
    elif exercise_type == ExerciseType.CONJUGATIONS:
        variations = [
            ("2nd_singular", "εσυ", "2-е лицо ед.ч. (εσυ)"),
            ("3rd_singular", "αυτος", "3-е лицо ед.ч. (αυτος/η/ο)"),
            ("1st_plural", "εμεις", "1-е лицо мн.ч. (εμεις)"),
            ("2nd_plural", "εσεις", "2-е лицо мн.ч. (εσεις)"),
            ("3rd_plural", "αυτοι", "3-е лицо мн.ч. (αυτοι/ες/α)"),
        ]
    else:  # CASES
        variations = [
            ("Γενικη", "родительный падеж (Γενικη)"),
            ("Αιτιατικη", "винительный падеж (Αιτιατικη)"),
            ("Κλητικη", "звательный падеж (Κλητικη)"),
        ]

    # Select word and variation
    if user_words:
        word_data, variation, new_history = self._select_word_and_variation(
            words=user_words,
            variations=variations,
            history=history,
        )
        is_from_ai = False
    else:
        word_data = await self._generate_word_with_ai(exercise_type)
        variation = random.choice(variations)
        new_history = history + [(word_data["word"], variation[0])]
        is_from_ai = True

    # Generate task with pre-selected variation
    task = await self._generate_task_details(
        exercise_type=exercise_type,
        word=word_data["word"],
        translation=word_data["translation"],
        is_from_ai=is_from_ai,
        selected_variation=variation,
    )

    return task, new_history
```

**Step 2.4:** Update handlers to pass history

**File:** `bot/telegram/handlers/exercises.py`

Update `start_exercise_session`:
```python
# Initialize session data
await state.update_data(
    exercise_type=exercise_type_str,
    total_count=0,
    correct_count=0,
    ai_words=[],
    user_words=user_words,
    current_task=None,
    exercise_history=[],  # NEW
)
```

Update `generate_and_show_task`:
```python
async def generate_and_show_task(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
):
    """Generate a new task and display it."""
    data = await state.get_data()
    exercise_type = ExerciseType(data.get("exercise_type"))
    user_words = data.get("user_words", [])
    total_count = data.get("total_count", 0)
    correct_count = data.get("correct_count", 0)
    history = data.get("exercise_history", [])  # NEW

    exercise_service = ExerciseService(session)

    # Generate task with history
    task, new_history = await exercise_service.generate_task(
        exercise_type=exercise_type,
        user_words=user_words if user_words else None,
        history=history,  # NEW
    )

    # Store current task and updated history
    await state.update_data(
        current_task={
            "word": task.word,
            "translation": task.translation,
            "task_text": task.task_text,
            "task_hint": task.task_hint,
            "expected_answer": task.expected_answer,
            "is_from_ai": task.is_from_ai,
        },
        exercise_history=new_history,  # NEW
    )
    # ... rest unchanged
```

### Phase 3: AI Word Supplementation

**Step 3.1:** Add supplementation method

**File:** `bot/services/exercise_service.py`

```python
# Configuration
MIN_WORDS_FOR_VARIETY = 3
AI_SUPPLEMENT_COUNT = 2

async def get_words_with_ai_supplement(
    self,
    user_id: int,
    exercise_type: ExerciseType,
) -> tuple[list[dict], list[dict]]:
    """Get words for exercises, supplementing with AI if needed.

    Args:
        user_id: User ID
        exercise_type: Type of exercise

    Returns:
        (all_words, ai_generated_words)
    """
    user_words = await self.get_user_words_for_exercise(
        user_id=user_id,
        exercise_type=exercise_type,
    )

    ai_words = []
    existing_word_texts = {w["word"] for w in user_words}

    if len(user_words) < MIN_WORDS_FOR_VARIETY:
        needed = min(AI_SUPPLEMENT_COUNT, MIN_WORDS_FOR_VARIETY - len(user_words))
        attempts = 0
        max_attempts = needed * 2  # Allow for duplicates

        while len(ai_words) < needed and attempts < max_attempts:
            attempts += 1
            ai_word = await self._generate_word_with_ai(exercise_type)
            if ai_word["word"] not in existing_word_texts:
                ai_words.append(ai_word)
                existing_word_texts.add(ai_word["word"])

    return user_words + ai_words, ai_words
```

**Step 3.2:** Update handler to use supplementation

**File:** `bot/telegram/handlers/exercises.py`

Update `start_exercise_session`:
```python
# Get user's words with AI supplement if needed
exercise_service = ExerciseService(session)
all_words, session_ai_words = await exercise_service.get_words_with_ai_supplement(
    user_id=user.id,
    exercise_type=exercise_type,
)

# Initialize session data
await state.update_data(
    exercise_type=exercise_type_str,
    total_count=0,
    correct_count=0,
    ai_words=session_ai_words,  # Start with any AI-generated supplements
    user_words=all_words,  # Include both user and AI words
    current_task=None,
    exercise_history=[],
)
```

---

## Testing Plan

### Unit Tests

**File:** `tests/test_services/test_exercise_service.py`

```python
class TestExerciseVariety:
    """Tests for exercise variety improvements."""

    async def test_tense_excludes_present(self, db_session):
        """Test that present tense is excluded from tense exercises."""
        service = ExerciseService(db_session)
        # Mock AI to return a known value
        tasks = []
        for _ in range(10):
            task = await service._generate_tense_task("γραφω", "писать", False)
            tasks.append(task)

        # Verify no task asks for present tense
        for task in tasks:
            assert task.task_hint != "Ενεστωτας"
            assert "настоящее время" not in task.task_text

    async def test_conjugation_excludes_first_singular(self, db_session):
        """Test that 1st person singular is excluded from conjugation exercises."""
        service = ExerciseService(db_session)
        tasks = []
        for _ in range(10):
            task = await service._generate_conjugation_task("γραφω", "писать", False)
            tasks.append(task)

        for task in tasks:
            assert task.task_hint != "εγω"

    async def test_case_excludes_nominative(self, db_session):
        """Test that nominative case is excluded from case exercises."""
        service = ExerciseService(db_session)
        tasks = []
        for _ in range(10):
            task = await service._generate_case_task("ο ανθρωπος", "человек", False)
            tasks.append(task)

        for task in tasks:
            assert task.task_hint != "Ονομαστικη"


class TestExerciseHistory:
    """Tests for exercise history tracking."""

    def test_select_avoids_recent(self):
        """Test that selection avoids recent combinations."""
        service = ExerciseService(None)  # Session not needed for this test

        words = [
            {"word": "γραφω", "translation": "писать"},
            {"word": "διαβαζω", "translation": "читать"},
        ]
        variations = [("A", "a"), ("B", "b")]
        history = [("γραφω", "A"), ("γραφω", "B")]

        # Should select διαβαζω since γραφω combinations are in history
        for _ in range(10):
            word, var, new_history = service._select_word_and_variation(
                words, variations, history
            )
            assert word["word"] == "διαβαζω"

    def test_history_cycles_when_exhausted(self):
        """Test that selection works when all combinations are in history."""
        service = ExerciseService(None)

        words = [{"word": "γραφω", "translation": "писать"}]
        variations = [("A", "a")]
        history = [("γραφω", "A")]  # Only combination is in history

        # Should still select (falls back)
        word, var, new_history = service._select_word_and_variation(
            words, variations, history
        )
        assert word["word"] == "γραφω"

    def test_history_limited_to_max_size(self):
        """Test that history doesn't grow beyond max size."""
        service = ExerciseService(None)

        words = [{"word": f"word{i}", "translation": f"trans{i}"} for i in range(20)]
        variations = [("A", "a")]
        history = []

        for _ in range(15):
            _, _, history = service._select_word_and_variation(
                words, variations, history
            )

        assert len(history) <= MAX_EXERCISE_HISTORY


class TestAISupplementation:
    """Tests for AI word supplementation."""

    async def test_supplements_when_below_threshold(self, db_session, mocker):
        """Test that AI words are added when user has few words."""
        service = ExerciseService(db_session)

        # Mock to return empty user words
        mocker.patch.object(
            service, 'get_user_words_for_exercise',
            return_value=[]
        )
        mocker.patch.object(
            service, '_generate_word_with_ai',
            return_value={"word": "γραφω", "translation": "писать"}
        )

        all_words, ai_words = await service.get_words_with_ai_supplement(
            user_id=1,
            exercise_type=ExerciseType.TENSES,
        )

        assert len(ai_words) > 0
        assert len(all_words) >= len(ai_words)

    async def test_no_supplement_when_enough_words(self, db_session, mocker):
        """Test that no AI words added when user has enough."""
        service = ExerciseService(db_session)

        user_words = [{"word": f"word{i}", "translation": f"trans{i}"} for i in range(5)]
        mocker.patch.object(
            service, 'get_user_words_for_exercise',
            return_value=user_words
        )

        all_words, ai_words = await service.get_words_with_ai_supplement(
            user_id=1,
            exercise_type=ExerciseType.TENSES,
        )

        assert len(ai_words) == 0
        assert all_words == user_words
```

---

## Migration Notes

No database migrations required. All changes are:
- Service layer logic modifications
- FSM state structure additions (not persisted)
- Handler flow updates

---

## Rollback Plan

If issues arise:
1. Revert changes to `exercise_service.py`
2. Revert changes to `exercises.py` handler
3. No data cleanup needed (FSM state is ephemeral)

---

## Performance Considerations

1. **History tracking:** O(n) for set creation, where n = history size (max 10)
2. **AI supplementation:** Additional API calls at session start (max 2 calls)
3. **Memory:** Minimal increase in FSM state size

---

## Future Enhancements

1. **Persist exercise history:** Track user's exercise history in database for long-term variety
2. **Adaptive difficulty:** Reduce variation exclusions as user improves
3. **Spaced repetition for grammar:** Track which grammar points need more practice
4. **User preferences:** Let users choose which tenses/cases to practice

---

## Summary

| Issue | Solution | Priority | Complexity |
|-------|----------|----------|------------|
| Question = Answer | Exclude source form from targets | High | Low |
| Same verb repeats | History tracking | High | Medium |
| Single verb in deck | AI word supplementation | Medium | Medium |

Total implementation estimate: 4-6 hours including tests.
