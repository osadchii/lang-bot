"""AI service for OpenAI integration."""

import json
from dataclasses import dataclass

from openai import APIConnectionError, APIError, APITimeoutError, AsyncOpenAI, RateLimitError

from bot.config.logging_config import get_logger
from bot.config.settings import settings
from bot.messages import ai as ai_messages


@dataclass
class ImageTextResult:
    """Result from image text recognition and processing."""

    recognized_text: str
    translation: str
    additional_response: str | None = None
    has_greek_text: bool = True


logger = get_logger(__name__)

# Prompts for message categorization
CATEGORIZATION_SYSTEM_PROMPT = """Ты - классификатор сообщений для бота изучения греческого языка.
Твоя задача - определить намерение пользователя и извлечь необходимые данные.

КАТЕГОРИИ:
1. word_translation - перевод ОДНОГО слова (греческий <-> русский)
   - Примеры: "калимера", "привет", "как переводится спити", "что значит вода"
   - Признаки: одиночное слово, просьба перевести слово, вопрос о значении слова

2. text_translation - перевод текста/предложения (более одного слова для перевода)
   - Примеры: "переведи 'я люблю Грецию'", "как будет по-гречески 'доброе утро, друг'"
   - Признаки: несколько слов для перевода, предложение, фраза

3. language_question - вопрос о греческом языке (грамматика, употребление, правила)
   - Примеры: "как образуется прошедшее время", "когда использовать артикль", "почему здесь винительный падеж"
   - Признаки: вопросы "почему", "как", "когда", "в чем разница", просьба объяснить

ВАЖНО:
- Если пользователь просто написал слово без контекста - это word_translation
- Если пользователь написал несколько слов без вопроса о языке - это text_translation
- Если пользователь задает вопрос о правилах языка - это language_question

Отвечай СТРОГО в формате JSON без дополнительного текста."""

CATEGORIZATION_USER_PROMPT = """Проанализируй сообщение пользователя и определи его намерение.

Сообщение: {message}

Ответь в формате JSON:
{{
    "category": "word_translation" | "text_translation" | "language_question" | "unknown",
    "confidence": 0.0-1.0,
    "extracted_content": "слово или текст для перевода / вопрос пользователя",
    "source_language": "greek" | "russian" | null,
    "topic": "grammar" | "vocabulary" | "pronunciation" | "usage" | null
}}

Примеры:
- "спити" -> {{"category": "word_translation", "confidence": 0.95, "extracted_content": "спити", "source_language": "greek", "topic": null}}
- "как переводится дом" -> {{"category": "word_translation", "confidence": 0.95, "extracted_content": "дом", "source_language": "russian", "topic": null}}
- "переведи 'я иду домой'" -> {{"category": "text_translation", "confidence": 0.90, "extracted_content": "я иду домой", "source_language": "russian", "topic": null}}
- "когда использовать о а когда и" -> {{"category": "language_question", "confidence": 0.90, "extracted_content": "когда использовать о а когда и", "source_language": null, "topic": "grammar"}}"""

WORD_EXTRACTION_SYSTEM_PROMPT = """Ты - лингвистический анализатор греческого языка.
Твоя задача - извлекать из фразы ТОЛЬКО значимые слова (content words) и приводить их к словарной форме.

ПРАВИЛА:
1. ПРОПУСКАЙ служебные слова:
   - Артикли: ο, η, το, οι, τα, τον, την, του, της, των, τους, τις, ένας, μια, ένα
   - Предлоги: σε, από, με, για, προς, κατά, μετά, χωρίς, μέχρι, ως, στον, στην, στο
   - Союзы: και, ή, αλλά, όμως, γιατί, επειδή, αν, όταν, ενώ, που
   - Частицы: να, θα, δεν, μη, ας
   - Местоимения-клитики: με, σε, τον, την, το, μας, σας, τους

2. ИЗВЛЕКАЙ значимые слова:
   - Существительные
   - Глаголы
   - Прилагательные
   - Наречия
   - Числительные (кроме один/два как артиклей)
   - Значимые местоимения (εγώ, εσύ, αυτός, etc.)

3. ПРИВОДИ К СЛОВАРНОЙ ФОРМЕ (lemma):
   - Существительные: именительный падеж, единственное число
   - Глаголы: 1 лицо, единственное число, настоящее время
   - Прилагательные: мужской род, единственное число

4. ДЛЯ СУЩЕСТВИТЕЛЬНЫХ добавляй артикль для указания рода:
   - ο (мужской), η (женский), το (средний)

5. ВСЕГДА используй СТРОЧНЫЕ буквы в lemma и lemma_with_article.

ФОРМАТ ОТВЕТА (JSON):
{
    "words": [
        {
            "original": "слово как в тексте",
            "lemma": "словарная форма (строчные)",
            "lemma_with_article": "артикль + lemma для существительных (строчные)",
            "translation": "перевод на русский",
            "pos": "noun|verb|adjective|adverb|pronoun|numeral"
        }
    ]
}"""

WORD_EXTRACTION_USER_PROMPT = """Извлеки значимые слова из фразы и приведи к словарной форме.

Фраза ({language}): {phrase}

Ответь ТОЛЬКО в формате JSON без дополнительного текста."""

# Prompts for sentence analysis and feedback
SENTENCE_ANALYSIS_SYSTEM_PROMPT = """Ты - эксперт по греческому и русскому языкам.
Твоя задача - проанализировать предложение на наличие ошибок и дать перевод.

ПРОВЕРЯЙ:
1. Грамматические ошибки (падежи, согласование, порядок слов, артикли)
2. Орфографические ошибки
3. Неправильное использование слов или выражений
4. Стилистические ошибки (если явные)

ВАЖНО:
- Будь СТРОГИМ, но СПРАВЕДЛИВЫМ
- Если предложение правильное - отметь is_correct: true
- Если есть ошибки - опиши их КРАТКО (1-2 предложения на русском)
- Всегда давай перевод на целевой язык
- Для греческих существительных указывай артикль

Отвечай СТРОГО в формате JSON."""

SENTENCE_ANALYSIS_USER_PROMPT = """Проанализируй предложение на {source_lang} и переведи на {target_lang}.

Предложение: {sentence}

Ответь в формате JSON:
{{
    "is_correct": true/false,
    "error_description": "краткое описание ошибки на русском" | null,
    "corrected_sentence": "исправленное предложение" | null,
    "translation": "перевод на {target_lang}"
}}

Примеры:
- Правильное: {{"is_correct": true, "error_description": null, "corrected_sentence": null, "translation": "перевод"}}
- С ошибкой: {{"is_correct": false, "error_description": "Ошибка в согласовании прилагательного.", "corrected_sentence": "исправленный вариант", "translation": "перевод исправленного"}}"""

# Prompt for photo text recognition
PHOTO_TEXT_SYSTEM_PROMPT = """Ты - ассистент для изучения греческого языка.
Твоя задача - распознать греческий текст на изображении и помочь пользователю.

ИНСТРУКЦИИ:
1. Найди и распознай ВЕСЬ греческий текст на изображении
2. Сохраняй оригинальное форматирование (переносы строк, пунктуацию)
3. Переведи текст на русский язык
4. Если пользователь дал инструкцию - выполни её

ТИПЫ ИЗОБРАЖЕНИЙ:
- Уличные вывески и указатели
- Страницы учебников
- Рукописные записи
- Документы и тексты

ФОРМАТ ОТВЕТА (JSON):
{
    "has_greek_text": true/false,
    "recognized_text": "распознанный греческий текст",
    "translation": "перевод на русский",
    "response": "ответ на запрос пользователя (если есть)" | null
}

ВАЖНО:
- Если греческого текста нет, установи has_greek_text: false
- Для существительных указывай артикли при переводе
- Если пользователь просит проверить домашнее задание, дай подробный feedback об ошибках
- Если просят объяснить грамматику, дай подробное объяснение
- Если просят выполнить упражнение, выполни его и объясни решение"""


class AIService:
    """Service for AI-powered features using OpenAI API."""

    def __init__(self):
        """Initialize AI service."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key, timeout=settings.openai_timeout)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature

    async def ask_question(
        self,
        message: str,
        context: str | None = None,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> str:
        """Ask a question to the AI assistant.

        Args:
            message: User's question
            context: Optional context for the conversation (legacy support)
            conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]

        Returns:
            AI's response
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты - полезный ассистент для изучения греческого языка. "
                        "Помогай пользователям учить греческий: отвечай на вопросы, объясняй грамматику, "
                        "делай переводы. Отвечай на русском языке, будь кратким и познавательным. "
                        "Для греческих существительных всегда указывай артикль (ο, η, το) для обозначения рода."
                    ),
                }
            ]

            if context:
                messages.append({"role": "system", "content": f"Контекст: {context}"})

            if conversation_history:
                messages.extend(conversation_history)

            messages.append({"role": "user", "content": message})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            return response.choices[0].message.content or "Не удалось сгенерировать ответ."

        except RateLimitError:
            logger.warning("OpenAI rate limit exceeded")
            return ai_messages.MSG_AI_RATE_LIMIT
        except APITimeoutError:
            logger.error("OpenAI request timeout")
            return ai_messages.MSG_AI_TIMEOUT
        except APIConnectionError:
            logger.error("Failed to connect to OpenAI")
            return ai_messages.MSG_AI_CONNECTION_ERROR
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return ai_messages.MSG_AI_SERVICE_ERROR
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return ai_messages.MSG_AI_UNEXPECTED_ERROR

    async def translate_word(
        self, word: str, from_lang: str = "greek", to_lang: str = "russian"
    ) -> str:
        """Translate a word or phrase between Greek and Russian.

        Args:
            word: Word or phrase to translate
            from_lang: Source language ('greek' or 'russian')
            to_lang: Target language ('greek' or 'russian')

        Returns:
            Translation with optional context
        """
        try:
            lang_names = {"greek": "греческого", "russian": "русского"}
            to_lang_names = {"greek": "греческий", "russian": "русский"}

            prompt = (
                f"Переведи следующее слово/фразу с {lang_names.get(from_lang, from_lang)} "
                f"на {to_lang_names.get(to_lang, to_lang)}. "
                f"Для греческих существительных укажи артикль (ο/η/το).\n"
                f"Дай перевод и краткое пояснение при необходимости:\n\n{word}"
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты - греческо-русский переводчик. Давай точные переводы. "
                            "Для греческих существительных всегда указывай определённый артикль "
                            "для обозначения рода."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.3,
            )

            return response.choices[0].message.content or "Перевод недоступен."

        except RateLimitError:
            logger.warning("OpenAI rate limit exceeded")
            return ai_messages.MSG_AI_RATE_LIMIT
        except APITimeoutError:
            logger.error("OpenAI request timeout")
            return ai_messages.MSG_AI_TIMEOUT
        except APIConnectionError:
            logger.error("Failed to connect to OpenAI")
            return ai_messages.MSG_AI_CONNECTION_ERROR
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return ai_messages.MSG_AI_SERVICE_ERROR
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return ai_messages.MSG_AI_UNEXPECTED_ERROR

    async def analyze_and_translate_sentence(
        self,
        sentence: str,
        source_language: str,
    ) -> dict:
        """Analyze sentence for errors and provide translation with feedback.

        Args:
            sentence: Sentence to analyze
            source_language: 'greek' or 'russian'

        Returns:
            Dictionary with:
            - is_correct: bool
            - error_description: str | None
            - corrected_sentence: str | None
            - translation: str
        """
        target_language = "russian" if source_language == "greek" else "greek"
        lang_names = {
            "greek": "греческом",
            "russian": "русском",
        }
        target_lang_names = {
            "greek": "греческий",
            "russian": "русский",
        }

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": SENTENCE_ANALYSIS_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": SENTENCE_ANALYSIS_USER_PROMPT.format(
                            source_lang=lang_names.get(source_language, source_language),
                            target_lang=target_lang_names.get(target_language, target_language),
                            sentence=sentence,
                        ),
                    },
                ],
                max_tokens=500,
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            result = json.loads(content)

            return {
                "is_correct": result.get("is_correct", True),
                "error_description": result.get("error_description"),
                "corrected_sentence": result.get("corrected_sentence"),
                "translation": result.get("translation", ""),
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse sentence analysis response: {e}")
            # Fall back to simple translation
            translation = await self.translate_word(sentence, source_language, target_language)
            return {
                "is_correct": True,
                "error_description": None,
                "corrected_sentence": None,
                "translation": translation,
            }
        except (RateLimitError, APITimeoutError, APIConnectionError, APIError) as e:
            logger.error(f"Sentence analysis API error: {e}")
            # Fall back to simple translation
            translation = await self.translate_word(sentence, source_language, target_language)
            return {
                "is_correct": True,
                "error_description": None,
                "corrected_sentence": None,
                "translation": translation,
            }
        except Exception as e:
            logger.exception(f"Sentence analysis failed: {e}")
            # Fall back to simple translation
            translation = await self.translate_word(sentence, source_language, target_language)
            return {
                "is_correct": True,
                "error_description": None,
                "corrected_sentence": None,
                "translation": translation,
            }

    async def explain_grammar(self, text: str) -> str:
        """Explain the grammar of a Greek sentence or phrase.

        Args:
            text: Greek text to explain

        Returns:
            Grammar explanation in Russian
        """
        try:
            prompt = (
                f"Объясни грамматику этого греческого текста простым языком:\n\n{text}\n\n"
                f"Включи:\n"
                f"1. Разбор слов\n"
                f"2. Грамматические конструкции\n"
                f"3. Ключевые грамматические правила"
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты - эксперт по греческой грамматике. Объясняй греческую грамматику "
                            "понятно и доступно для изучающих язык. Отвечай на русском языке."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=0.5,
            )

            return response.choices[0].message.content or "Объяснение грамматики недоступно."

        except RateLimitError:
            logger.warning("OpenAI rate limit exceeded")
            return ai_messages.MSG_AI_RATE_LIMIT
        except APITimeoutError:
            logger.error("OpenAI request timeout")
            return ai_messages.MSG_AI_TIMEOUT
        except APIConnectionError:
            logger.error("Failed to connect to OpenAI")
            return ai_messages.MSG_AI_CONNECTION_ERROR
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return ai_messages.MSG_AI_SERVICE_ERROR
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return ai_messages.MSG_AI_UNEXPECTED_ERROR

    async def generate_card_from_word(
        self, word: str, source_language: str = "greek"
    ) -> dict[str, str]:
        """Generate a flashcard from a word in Greek or Russian.

        Args:
            word: Word to create card from
            source_language: 'greek' or 'russian'

        Returns:
            Dictionary with 'front' (Greek with article), 'back' (Russian), 'example' fields
        """
        try:
            if source_language == "russian":
                prompt = (
                    f"Создай карточку для изучения греческого слова по русскому слову: {word}\n\n"
                    f"Предоставь:\n"
                    f"1. Греческий перевод С АРТИКЛЕМ (ο/η/το для существительных)\n"
                    f"2. Исходное русское слово\n"
                    f"3. Пример предложения на греческом с русским переводом\n\n"
                    f"ВАЖНО: Для существительных ОБЯЗАТЕЛЬНО укажи греческий артикль "
                    f"(ο для мужского рода, η для женского, το для среднего).\n\n"
                    f"Формат ответа:\n"
                    f"FRONT: [греческое слово с артиклем если существительное]\n"
                    f"BACK: [русское слово]\n"
                    f"EXAMPLE: [пример на греческом] - [русский перевод]"
                )
            else:
                prompt = (
                    f"Создай карточку для изучения греческого слова: {word}\n\n"
                    f"Предоставь:\n"
                    f"1. Греческое слово С АРТИКЛЕМ (ο/η/το для существительных)\n"
                    f"2. Русский перевод\n"
                    f"3. Пример предложения на греческом с русским переводом\n\n"
                    f"ВАЖНО: Для существительных ОБЯЗАТЕЛЬНО укажи греческий артикль "
                    f"(ο для мужского рода, η для женского, το для среднего).\n"
                    f"Если во вводе нет артикля, добавь правильный.\n\n"
                    f"Формат ответа:\n"
                    f"FRONT: [греческое слово с артиклем если существительное]\n"
                    f"BACK: [русский перевод]\n"
                    f"EXAMPLE: [пример на греческом] - [русский перевод]"
                )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты - эксперт по греческому языку, помогающий русскоязычным "
                            "изучать греческий. Всегда давай точные переводы и убедись, что "
                            "греческие существительные включают артикль (ο, η, το) для указания "
                            "грамматического рода. Отвечай строго в запрошенном формате."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.7,
            )

            content = response.choices[0].message.content or ""

            # Parse the response
            front = ""
            back = ""
            example = ""

            for line in content.split("\n"):
                if line.startswith("FRONT:"):
                    front = line.replace("FRONT:", "").strip()
                elif line.startswith("BACK:"):
                    back = line.replace("BACK:", "").strip()
                elif line.startswith("EXAMPLE:"):
                    example = line.replace("EXAMPLE:", "").strip()

            return {"front": front or word, "back": back or "", "example": example or ""}

        except RateLimitError:
            logger.warning("OpenAI rate limit exceeded")
            return {
                "front": word,
                "back": ai_messages.MSG_AI_RATE_LIMIT,
                "example": "",
            }
        except APITimeoutError:
            logger.error("OpenAI request timeout")
            return {"front": word, "back": ai_messages.MSG_AI_TIMEOUT, "example": ""}
        except APIConnectionError:
            logger.error("Failed to connect to OpenAI")
            return {"front": word, "back": ai_messages.MSG_AI_CONNECTION_ERROR, "example": ""}
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return {"front": word, "back": ai_messages.MSG_AI_SERVICE_ERROR, "example": ""}
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return {"front": word, "back": "", "example": ""}

    async def generate_example_sentence(self, word: str) -> str:
        """Generate an example sentence using a Greek word.

        Args:
            word: Greek word

        Returns:
            Example sentence with Russian translation
        """
        try:
            prompt = (
                f"Создай простое примерное предложение на греческом, используя слово: {word}\n"
                f"Предоставь греческое предложение и его русский перевод."
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты - преподаватель греческого языка, создающий примеры предложений. "
                            "Отвечай на русском языке."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
                temperature=0.7,
            )

            return response.choices[0].message.content or ""

        except RateLimitError:
            logger.warning("OpenAI rate limit exceeded")
            return ai_messages.MSG_AI_RATE_LIMIT
        except APITimeoutError:
            logger.error("OpenAI request timeout")
            return ai_messages.MSG_AI_TIMEOUT
        except APIConnectionError:
            logger.error("Failed to connect to OpenAI")
            return ai_messages.MSG_AI_CONNECTION_ERROR
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return ai_messages.MSG_AI_SERVICE_ERROR
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return ""

    async def suggest_deck_for_word(
        self,
        word: str,
        translation: str,
        deck_names: list[str],
    ) -> str | None:
        """Suggest the most suitable deck for a word from existing decks.

        Args:
            word: Greek word
            translation: Russian translation
            deck_names: List of user's existing deck names

        Returns:
            Best matching deck name or None if no suitable deck
        """
        if not deck_names:
            return None

        try:
            prompt = (
                f"Слово: {word} ({translation})\n\n"
                f"Колоды пользователя: {', '.join(deck_names)}\n\n"
                f"Какая колода лучше всего подходит для этого слова по смыслу/категории?\n"
                f"Ответь ТОЛЬКО названием колоды из списка или NONE если ни одна не подходит."
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты помогаешь сортировать слова по тематическим колодам. "
                            "Отвечай только названием колоды или NONE."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=50,
                temperature=0.3,
            )

            result = response.choices[0].message.content or ""
            result = result.strip()

            if result.upper() == "NONE":
                return None

            # Find matching deck (case-insensitive)
            for name in deck_names:
                if name.lower() == result.lower():
                    return name

            return None

        except Exception as e:
            logger.warning(f"Failed to suggest deck: {e}")
            return None

    async def generate_deck_name(self, word: str, translation: str) -> str:
        """Generate a suitable deck name for a word category.

        Args:
            word: Greek word
            translation: Russian translation

        Returns:
            Suggested deck name in Russian
        """
        try:
            prompt = (
                f"Слово: {word} ({translation})\n\n"
                f"Придумай короткое название колоды на русском для категории этого слова.\n"
                f"Например: Еда, Транспорт, Семья, Одежда, Дом, Работа.\n"
                f"Ответь ТОЛЬКО названием (1-3 слова), без пояснений."
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты генерируешь короткие названия категорий. Отвечай только названием.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=30,
                temperature=0.5,
            )

            result = response.choices[0].message.content or "Разное"
            return result.strip()[:50]

        except Exception as e:
            logger.warning(f"Failed to generate deck name: {e}")
            return "Разное"

    async def categorize_message(self, message: str) -> dict:
        """Categorize a user message to determine intent.

        Args:
            message: User's message text

        Returns:
            Dictionary with category, confidence, and extracted data

        Raises:
            Exception: If API call fails or response cannot be parsed
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": CATEGORIZATION_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": CATEGORIZATION_USER_PROMPT.format(message=message),
                    },
                ],
                max_tokens=200,
                temperature=0.2,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            return json.loads(content)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI categorization response: {e}")
            raise
        except (RateLimitError, APITimeoutError, APIConnectionError, APIError) as e:
            logger.error(f"AI categorization API error: {e}")
            raise

    async def extract_and_lemmatize_words(
        self,
        phrase: str,
        source_language: str,
    ) -> list[dict]:
        """Extract content words from phrase and return their lemmas.

        Args:
            phrase: Phrase to extract words from
            source_language: 'greek' or 'russian'

        Returns:
            List of word dictionaries with:
            - original: word as it appears in phrase
            - lemma: base/dictionary form (lowercase)
            - lemma_with_article: for nouns, includes article
            - translation: Russian translation (if Greek) or Greek (if Russian)
            - pos: part of speech
        """
        try:
            lang_names = {"greek": "греческий", "russian": "русский"}
            prompt = WORD_EXTRACTION_USER_PROMPT.format(
                language=lang_names.get(source_language, source_language),
                phrase=phrase,
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": WORD_EXTRACTION_SYSTEM_PROMPT,
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1000,
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            result = json.loads(content)
            return result.get("words", [])

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse word extraction response: {e}")
            return []
        except (RateLimitError, APITimeoutError, APIConnectionError, APIError) as e:
            logger.error(f"Word extraction API error: {e}")
            return []
        except Exception as e:
            logger.exception(f"Word extraction failed: {e}")
            return []

    async def process_image_text(
        self,
        image_base64: str,
        user_prompt: str | None = None,
    ) -> ImageTextResult:
        """Process image containing Greek text.

        Uses OpenAI Vision API to recognize Greek text from images
        and optionally process it according to user's prompt.

        Args:
            image_base64: Base64-encoded image data
            user_prompt: Optional user instruction (e.g., "check homework")

        Returns:
            ImageTextResult with recognized text and processing results
        """
        try:
            # Type hint needed because messages can have string or list content
            messages: list[dict] = [
                {
                    "role": "system",
                    "content": PHOTO_TEXT_SYSTEM_PROMPT,
                }
            ]

            # Build user message with image
            user_content: list[dict] = [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}",
                        "detail": "high",
                    },
                },
            ]

            text = (
                f"Запрос пользователя: {user_prompt}"
                if user_prompt
                else "Распознай греческий текст на изображении и переведи на русский."
            )
            user_content.append({"type": "text", "text": text})

            messages.append({"role": "user", "content": user_content})

            response = await self.client.chat.completions.create(
                model=settings.openai_vision_model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            result = json.loads(content)

            return ImageTextResult(
                recognized_text=result.get("recognized_text", ""),
                translation=result.get("translation", ""),
                additional_response=result.get("response"),
                has_greek_text=result.get("has_greek_text", False),
            )

        except RateLimitError:
            logger.warning("OpenAI rate limit exceeded for vision request")
            return ImageTextResult(
                recognized_text="",
                translation=ai_messages.MSG_AI_RATE_LIMIT,
                has_greek_text=False,
            )
        except APITimeoutError:
            logger.error("OpenAI vision request timeout")
            return ImageTextResult(
                recognized_text="",
                translation=ai_messages.MSG_AI_TIMEOUT,
                has_greek_text=False,
            )
        except APIConnectionError:
            logger.error("Failed to connect to OpenAI for vision")
            return ImageTextResult(
                recognized_text="",
                translation=ai_messages.MSG_AI_CONNECTION_ERROR,
                has_greek_text=False,
            )
        except APIError as e:
            logger.error(f"OpenAI Vision API error: {e}")
            return ImageTextResult(
                recognized_text="",
                translation=ai_messages.MSG_AI_SERVICE_ERROR,
                has_greek_text=False,
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse vision response: {e}")
            return ImageTextResult(
                recognized_text="",
                translation=ai_messages.MSG_AI_UNEXPECTED_ERROR,
                has_greek_text=False,
            )
