"""AI service for OpenAI integration."""

from openai import APIConnectionError, APIError, APITimeoutError, AsyncOpenAI, RateLimitError

from bot.config.logging_config import get_logger
from bot.config.settings import settings
from bot.messages import ai as ai_messages

logger = get_logger(__name__)


class AIService:
    """Service for AI-powered features using OpenAI API."""

    def __init__(self):
        """Initialize AI service."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key, timeout=settings.openai_timeout)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature

    async def ask_question(self, message: str, context: str | None = None) -> str:
        """Ask a question to the AI assistant.

        Args:
            message: User's question
            context: Optional context for the conversation

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
