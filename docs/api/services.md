# Services API Reference

## Overview

Services contain business logic and orchestrate operations between handlers and repositories. All services follow the same initialization pattern: they receive `AsyncSession` and create necessary repositories.

**Note**: This bot is designed for **Russian-speaking users** learning **Greek**. All AI prompts and responses are in Russian.

## Common Pattern

```python
class ServiceName:
    def __init__(self, session: AsyncSession):
        self.repo = SomeRepository(session)
        self.session = session

    async def method_name(self, param: Type) -> ReturnType:
        # Business logic
        pass
```

---

## UserService

**File**: `bot/services/user_service.py`

Manages user accounts and user-related operations.

### Methods

#### `get_or_create_user(telegram_id: int, **kwargs) -> tuple[User, bool]`

Get existing user or create new one.

**Parameters**:
- `telegram_id` (int): Telegram user ID
- `**kwargs`: Additional user fields (username, first_name, language_code)

**Returns**: Tuple of (User, created) where created is bool

**Example**:
```python
from bot.services.user_service import UserService

user_service = UserService(session)
user, was_created = await user_service.get_or_create_user(
    telegram_id=123456789,
    username="john_doe",
    first_name="John"
)
```

---

## DeckService

**File**: `bot/services/deck_service.py`

Handles deck management operations.

### Methods

#### `create_deck(user_id: int, name: str, description: str = None) -> Deck`

Create a new deck for a user.

**Parameters**:
- `user_id` (int): User ID
- `name` (str): Deck name (max 255 chars)
- `description` (str, optional): Deck description

**Returns**: Created Deck instance

**Raises**:
- `ValueError`: If deck name is empty or too long
- `IntegrityError`: If deck with same name already exists for user

**Example**:
```python
deck_service = DeckService(session)
deck = await deck_service.create_deck(
    user_id=1,
    name="Greek Basics",
    description="Essential Greek vocabulary"
)
```

#### `get_user_decks(user_id: int) -> list[Deck]`

Get all decks for a user.

**Example**:
```python
decks = await deck_service.get_user_decks(user_id=1)
```

#### `get_deck_with_stats(deck_id: int) -> tuple[Deck | None, int]`

Get deck with card count.

**Returns**: Tuple of (Deck, card_count)

---

## CardService

**File**: `bot/services/card_service.py`

Manages flashcard operations.

### Methods

#### `create_card(deck_id: int, front: str, back: str, example: str = None, notes: str = None) -> Card`

Create a new flashcard.

**Parameters**:
- `deck_id` (int): Deck to add card to
- `front` (str): Front of card (question/word)
- `back` (str): Back of card (answer/translation)
- `example` (str, optional): Example usage
- `notes` (str, optional): Additional notes

**Returns**: Created Card instance

**Example**:
```python
card_service = CardService(session)
card = await card_service.create_card(
    deck_id=1,
    front="Γεια σου",
    back="Hello (informal)",
    example="Γεια σου, τι κάνεις; - Hello, how are you?"
)
```

#### `get_deck_cards(deck_id: int, limit: int = 100, offset: int = 0) -> list[Card]`

Get cards from a deck with pagination.

---

## LearningService

**File**: `bot/services/learning_service.py`

Handles learning sessions and spaced repetition.

### Methods

#### `get_learning_session(deck_id: int, max_cards: int = 20, max_new_cards: int = 20) -> list[Card]`

Get cards for a learning session.

**Parameters**:
- `deck_id` (int): Deck to learn from
- `max_cards` (int): Maximum total cards (default: 20)
- `max_new_cards` (int): Maximum new cards to include (default: 20)

**Returns**: List of Card instances (mix of due and new cards)

**Example**:
```python
learning_service = LearningService(session)
cards = await learning_service.get_learning_session(
    deck_id=1,
    max_cards=20,
    max_new_cards=10
)
```

#### `process_card_review(card_id: int, user_id: int, quality: int, time_spent: int = None) -> Card`

Process a card review and update SRS data.

**Parameters**:
- `card_id` (int): Card being reviewed
- `user_id` (int): User reviewing the card
- `quality` (int): Quality rating (0=Forgot, 3=Remembered, 5=Easy)
- `time_spent` (int, optional): Time spent in seconds

**Returns**: Updated Card instance

**Raises**:
- `ValueError`: If card not found or SRS calculation fails

**Example**:
```python
# User rates card as "Remembered" (3)
card = await learning_service.process_card_review(
    card_id=123,
    user_id=1,
    quality=3,
    time_spent=15
)
print(f"Next review: {card.next_review}")
```

#### `get_deck_stats(deck_id: int) -> dict`

Get statistics for a deck.

**Returns**: Dictionary with:
- `total_cards`: Total number of cards
- `new_cards`: Number of new cards (repetitions=0)
- `due_cards`: Number of cards due for review
- `learning_cards`: Number of cards in learning (total - new)

**Example**:
```python
stats = await learning_service.get_deck_stats(deck_id=1)
print(f"Total: {stats['total_cards']}, Due: {stats['due_cards']}")
```

---

## AIService

**File**: `bot/services/ai_service.py`

OpenAI API integration for AI-powered features. All responses are in Russian for Russian-speaking users.

### Methods

#### `ask_question(message: str, context: str = None, conversation_history: list[dict[str, str]] = None) -> str`

Ask a question to the AI assistant with optional conversation history.

**Parameters**:
- `message` (str): User's question
- `context` (str, optional): Additional context (legacy support)
- `conversation_history` (list, optional): List of previous messages `[{"role": "user/assistant", "content": "..."}]`

**Returns**: AI's response as string (in Russian)

**Example**:
```python
ai_service = AIService()

# Simple question
response = await ai_service.ask_question(
    "В чем разница между και и αλλά?"
)

# With conversation history
history = [
    {"role": "user", "content": "Как сказать 'привет'?"},
    {"role": "assistant", "content": "Γεια σου (ghia su) - неформальное приветствие"}
]
response = await ai_service.ask_question(
    "А как сказать 'до свидания'?",
    conversation_history=history
)
```

#### `translate_word(word: str, from_lang: str = "greek", to_lang: str = "russian") -> str`

Translate a word or phrase between Greek and Russian.

**Parameters**:
- `word` (str): Word or phrase to translate
- `from_lang` (str): Source language ('greek' or 'russian')
- `to_lang` (str): Target language ('greek' or 'russian')

**Returns**: Translation with context (in Russian)

**Example**:
```python
# Greek to Russian
translation = await ai_service.translate_word("καλημέρα")
# Returns: "Доброе утро (формальное приветствие)"

# Russian to Greek
translation = await ai_service.translate_word("привет", from_lang="russian", to_lang="greek")
# Returns: "Γεια σου (ghia su) - неформальное приветствие"
```

#### `explain_grammar(text: str) -> str`

Explain the grammar of Greek text in Russian.

**Parameters**:
- `text` (str): Greek text to explain

**Returns**: Grammar explanation in Russian

**Example**:
```python
explanation = await ai_service.explain_grammar("Το βιβλίο είναι ενδιαφέρον")
```

#### `generate_card_from_word(word: str, source_language: str = "greek") -> dict[str, str]`

Generate a flashcard from a word in Greek or Russian.

**Parameters**:
- `word` (str): Word to create card from
- `source_language` (str): 'greek' or 'russian'

**Returns**: Dictionary with keys:
- `front`: Greek word with article (for nouns: ο/η/το)
- `back`: Russian translation
- `example`: Example sentence

**Example**:
```python
# From Greek word
card_data = await ai_service.generate_card_from_word("αγάπη")
# Returns: {"front": "η αγάπη", "back": "любовь", "example": "..."}

# From Russian word
card_data = await ai_service.generate_card_from_word("дом", source_language="russian")
# Returns: {"front": "το σπίτι", "back": "дом", "example": "..."}
```

#### `generate_example_sentence(word: str) -> str`

Generate an example sentence using a Greek word.

**Parameters**:
- `word` (str): Greek word

**Returns**: Example sentence with Russian translation

**Example**:
```python
example = await ai_service.generate_example_sentence("σπίτι")
```

#### `suggest_deck_for_word(word: str, translation: str, deck_names: list[str]) -> str | None`

Suggest the most suitable deck for a word from existing decks.

**Parameters**:
- `word` (str): Greek word
- `translation` (str): Russian translation
- `deck_names` (list[str]): List of user's existing deck names

**Returns**: Best matching deck name or None if no suitable deck

**Example**:
```python
suggested = await ai_service.suggest_deck_for_word(
    word="το σπίτι",
    translation="дом",
    deck_names=["Еда", "Транспорт", "Дом и семья"]
)
# Returns: "Дом и семья"
```

#### `generate_deck_name(word: str, translation: str) -> str`

Generate a suitable deck name for a word category.

**Parameters**:
- `word` (str): Greek word
- `translation` (str): Russian translation

**Returns**: Suggested deck name in Russian

**Example**:
```python
name = await ai_service.generate_deck_name("το αυτοκίνητο", "автомобиль")
# Returns: "Транспорт"
```

#### `categorize_message(message: str) -> dict`

Categorize a user message to determine intent using AI.

**Parameters**:
- `message` (str): User's message text

**Returns**: Dictionary with:
- `category`: "word_translation" | "text_translation" | "language_question" | "unknown"
- `confidence`: 0.0-1.0
- `extracted_content`: Word/text/question extracted from message
- `source_language`: "greek" | "russian" | null
- `topic`: "grammar" | "vocabulary" | "pronunciation" | "usage" | null

**Raises**: Exception if API call fails or response cannot be parsed

**Example**:
```python
result = await ai_service.categorize_message("как переводится σπίτι")
# Returns: {
#     "category": "word_translation",
#     "confidence": 0.95,
#     "extracted_content": "σπίτι",
#     "source_language": "greek",
#     "topic": null
# }
```

---

## ConversationService

**File**: `bot/services/conversation_service.py`

Manages AI conversation history for context-aware responses.

### Methods

#### `add_user_message(user: User, content: str, conversation_id: str = "default", message_type: str = None) -> ConversationMessage`

Add a user message to the conversation history.

**Parameters**:
- `user` (User): User model instance
- `content` (str): Message content
- `conversation_id` (str): Conversation identifier (default: "default")
- `message_type` (str, optional): Type of interaction (e.g., "ask_question", "translate")

**Returns**: Created ConversationMessage instance

**Example**:
```python
conv_service = ConversationService(session)
msg = await conv_service.add_user_message(
    user=user,
    content="Как сказать 'привет' по-гречески?",
    message_type="ask_question"
)
```

#### `add_assistant_message(user: User, content: str, conversation_id: str = "default", message_type: str = None, token_count: int = None) -> ConversationMessage`

Add an assistant (AI) message to the conversation history.

**Parameters**:
- `user` (User): User model instance
- `content` (str): Message content
- `conversation_id` (str): Conversation identifier
- `message_type` (str, optional): Type of interaction
- `token_count` (int, optional): Optional token usage

**Returns**: Created ConversationMessage instance

#### `get_context_messages(user: User, conversation_id: str = "default", limit: int = None) -> list[dict[str, str]]`

Get recent messages formatted for OpenAI API.

**Parameters**:
- `user` (User): User model instance
- `conversation_id` (str): Conversation identifier
- `limit` (int, optional): Number of messages (uses setting if not provided)

**Returns**: List of message dicts with 'role' and 'content' keys

**Example**:
```python
history = await conv_service.get_context_messages(user)
# Returns: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

# Use with AIService
response = await ai_service.ask_question(
    message="А как сказать 'пока'?",
    conversation_history=history
)
```

#### `clear_conversation(user: User, conversation_id: str = "default") -> int`

Clear conversation history for a user.

**Parameters**:
- `user` (User): User model instance
- `conversation_id` (str): Conversation identifier

**Returns**: Number of messages deleted

#### `get_conversation_stats(user: User, conversation_id: str = "default") -> dict[str, int]`

Get conversation statistics.

**Returns**: Dictionary with `total_messages` count

#### `cleanup_old_messages(days: int = None) -> int`

Cleanup old messages across all users.

**Parameters**:
- `days` (int, optional): Age threshold (uses setting if not provided)

**Returns**: Number of messages deleted

---

## TranslationService

**File**: `bot/services/translation_service.py`

Smart translation service that integrates with user's cards.

### Data Classes

#### `TranslationResult`

Result of a translation request.

| Field | Type | Description |
|-------|------|-------------|
| `word` | str | Original word |
| `source_language` | str | 'greek' or 'russian' |
| `translation` | str | AI translation response |
| `existing_card` | Card \| None | Found card if exists |
| `existing_deck` | Deck \| None | Deck containing the card |
| `existing_count` | int | Number of decks containing the word |
| `suggested_deck` | Deck \| None | AI-suggested deck for new card |
| `suggested_deck_name` | str \| None | Suggested name if no suitable deck |

#### `CardData`

Data for creating a card from translation.

| Field | Type | Description |
|-------|------|-------------|
| `front` | str | Greek with article |
| `back` | str | Russian translation |
| `example` | str | Example sentence |

### Methods

#### `translate_with_card_check(user: User, word: str, source_language: str) -> TranslationResult`

Translate word and check if it exists in user's cards.

**Parameters**:
- `user` (User): User making the request
- `word` (str): Word to translate
- `source_language` (str): 'greek' or 'russian'

**Returns**: TranslationResult with all relevant data

**Example**:
```python
trans_service = TranslationService(session)
result = await trans_service.translate_with_card_check(
    user=user,
    word="σπίτι",
    source_language="greek"
)

if result.existing_card:
    print(f"Card exists in deck: {result.existing_deck.name}")
else:
    print(f"Suggested deck: {result.suggested_deck.name or result.suggested_deck_name}")
```

#### `generate_card_data(word: str, source_language: str) -> CardData`

Generate card data from a word.

**Parameters**:
- `word` (str): Word to create card from
- `source_language` (str): 'greek' or 'russian'

**Returns**: CardData with front, back, and example

**Example**:
```python
card_data = await trans_service.generate_card_data("привет", "russian")
# card_data.front = "γεια σου"
# card_data.back = "привет"
# card_data.example = "Γεια σου, τι κάνεις;"
```

---

## MessageCategorizationService

**File**: `bot/services/message_categorization_service.py`

AI-powered message categorization for intent detection.

### Methods

#### `categorize_message(message: str) -> CategorizationResult`

Categorize a user message using AI.

**Parameters**:
- `message` (str): User's message text

**Returns**: CategorizationResult with category, confidence, and intent data

**Categories**:
- `WORD_TRANSLATION`: Single word translation request
- `TEXT_TRANSLATION`: Sentence/phrase translation
- `LANGUAGE_QUESTION`: Grammar or language usage question
- `UNKNOWN`: Could not determine intent

**Example**:
```python
categorization_service = MessageCategorizationService()
result = await categorization_service.categorize_message("как переводится дом")

if result.category == MessageCategory.WORD_TRANSLATION:
    intent = result.intent  # WordTranslationIntent
    print(f"Translate word: {intent.word} from {intent.source_language}")
elif result.category == MessageCategory.LANGUAGE_QUESTION:
    intent = result.intent  # LanguageQuestionIntent
    print(f"Question: {intent.question}, topic: {intent.topic}")
```

---

## ExerciseService

**File**: `bot/services/exercise_service.py`

Handles grammar exercise sessions for practicing Greek verb tenses, conjugations, and noun cases.

### Enums

#### `ExerciseType`

Types of grammar exercises:
- `TENSES`: Verb conjugation in different tenses (Present, Aorist, Future)
- `CONJUGATIONS`: Verb conjugation for different persons (1st/2nd/3rd singular/plural)
- `CASES`: Noun declension (Nominative, Genitive, Accusative, Vocative)

### Data Classes

#### `ExerciseTask`

A single exercise task.

| Field | Type | Description |
|-------|------|-------------|
| `word` | str | Greek word |
| `translation` | str | Russian translation |
| `task_text` | str | Task description in Russian |
| `task_hint` | str | Grammar hint (e.g., "Aoristos") |
| `expected_answer` | str | Correct answer |
| `is_from_ai` | bool | Whether word was generated by AI |

#### `AnswerResult`

Result of answer verification.

| Field | Type | Description |
|-------|------|-------------|
| `is_correct` | bool | Whether answer is correct |
| `feedback` | str | Grammar explanation in Russian |
| `correct_answer` | str | The correct answer |

### Methods

#### `get_user_words_for_exercise(user_id: int, exercise_type: ExerciseType, limit: int = 50) -> list[dict]`

Get words from user's cards suitable for the exercise type.

**Parameters**:
- `user_id` (int): User ID
- `exercise_type` (ExerciseType): Type of exercise
- `limit` (int): Maximum words to fetch

**Returns**: List of dicts with 'word' and 'translation' keys

**Example**:
```python
exercise_service = ExerciseService(session)
words = await exercise_service.get_user_words_for_exercise(
    user_id=1,
    exercise_type=ExerciseType.TENSES
)
# Returns: [{"word": "γραφω", "translation": "писать"}, ...]
```

#### `generate_task(exercise_type: ExerciseType, user_words: list[dict] | None = None) -> ExerciseTask`

Generate an exercise task. Uses user's words first, falls back to AI generation.

**Parameters**:
- `exercise_type` (ExerciseType): Type of exercise
- `user_words` (list[dict], optional): List of user's words

**Returns**: ExerciseTask with task details

**Example**:
```python
task = await exercise_service.generate_task(
    exercise_type=ExerciseType.CONJUGATIONS,
    user_words=[{"word": "γραφω", "translation": "писать"}]
)
# task.word = "γραφω"
# task.task_text = "Спрягай для 2-е лицо ед.ч. (εσυ)"
# task.expected_answer = "γραφεις"
```

#### `verify_answer(task: ExerciseTask, user_answer: str, exercise_type: ExerciseType) -> AnswerResult`

Verify user's answer and provide feedback using AI.

**Parameters**:
- `task` (ExerciseTask): The exercise task
- `user_answer` (str): User's answer
- `exercise_type` (ExerciseType): Type of exercise

**Returns**: AnswerResult with correctness and grammar feedback

**Example**:
```python
result = await exercise_service.verify_answer(
    task=task,
    user_answer="γραφεις",
    exercise_type=ExerciseType.CONJUGATIONS
)
# result.is_correct = True
# result.feedback = "Правильно! Глагол γραφω относится к первому спряжению..."
```

---

## StatisticsService

**File**: `bot/services/statistics_service.py`

Provides analytics and statistics.

### Methods

#### `get_user_stats(user_id: int) -> dict`

Get overall statistics for a user.

**Returns**: Dictionary with various statistics

**Example**:
```python
stats_service = StatisticsService(session)
stats = await stats_service.get_user_stats(user_id=1)
```

---

## Error Handling

All services handle errors appropriately:

### OpenAI Service Errors

```python
try:
    response = await ai_service.ask_question("...")
except Exception as e:
    # Returns user-friendly error message
    # Specific exceptions: RateLimitError, APITimeoutError, etc.
```

### Database Errors

```python
try:
    deck = await deck_service.create_deck(...)
except IntegrityError:
    # Handle duplicate deck name
except ValueError:
    # Handle validation errors
```

## Best Practices

1. **Always use services from handlers** - Never call repositories directly
2. **Pass AsyncSession to constructor** - Services manage their own repositories
3. **Trust service validation** - Services validate input before database operations
4. **Handle returned exceptions** - Services raise meaningful exceptions
5. **Use type hints** - All service methods are fully typed

## Further Reading

- [Repository API](./repositories.md) - Data access layer
- [Service Layer Architecture](../architecture/service-layer.md) - Design patterns
- [Handler Reference](./handlers.md) - How handlers use services
- [Message Categories](../architecture/message-categories.md) - Categorization types

---

**Last Updated**: 2026-01-21
**Maintained by**: Documentation Agent
