"""AI service for OpenAI integration."""

from openai import APIConnectionError, APIError, APITimeoutError, AsyncOpenAI, RateLimitError

from bot.config.logging_config import get_logger
from bot.config.settings import settings

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
                        "You are a helpful Greek language learning assistant. "
                        "Help users learn Greek by answering questions, explaining grammar, "
                        "and providing translations. Be concise and educational."
                    ),
                }
            ]

            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})

            messages.append({"role": "user", "content": message})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            return response.choices[0].message.content or "I couldn't generate a response."

        except RateLimitError:
            logger.warning("OpenAI rate limit exceeded")
            return "I'm receiving too many requests right now. Please wait about a minute and try again."
        except APITimeoutError:
            logger.error("OpenAI request timeout")
            return "Your request took too long to process. Please try again with a simpler query."
        except APIConnectionError:
            logger.error("Failed to connect to OpenAI")
            return "I'm having trouble connecting to the AI service. Please check your internet connection and try again."
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return "AI service error. Please try again."
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return "Unexpected error occurred. Please try again later."

    async def translate_word(
        self, word: str, from_lang: str = "greek", to_lang: str = "english"
    ) -> str:
        """Translate a word or phrase.

        Args:
            word: Word or phrase to translate
            from_lang: Source language
            to_lang: Target language

        Returns:
            Translation with optional context
        """
        try:
            prompt = (
                f"Translate the following {from_lang} word/phrase to {to_lang}. "
                f"Provide the translation and a brief explanation if needed:\n\n{word}"
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Greek-English translator. Provide accurate translations.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.3,  # Lower temperature for more consistent translations
            )

            return response.choices[0].message.content or "Translation not available."

        except RateLimitError:
            logger.warning("OpenAI rate limit exceeded")
            return "I'm receiving too many requests right now. Please wait about a minute and try again."
        except APITimeoutError:
            logger.error("OpenAI request timeout")
            return "Your request took too long to process. Please try again with a simpler query."
        except APIConnectionError:
            logger.error("Failed to connect to OpenAI")
            return "I'm having trouble connecting to the AI service. Please check your internet connection and try again."
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return "AI service error. Please try again."
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return "Unexpected error occurred. Please try again later."

    async def explain_grammar(self, text: str) -> str:
        """Explain the grammar of a Greek sentence or phrase.

        Args:
            text: Greek text to explain

        Returns:
            Grammar explanation
        """
        try:
            prompt = (
                f"Explain the grammar of this Greek text in simple terms:\n\n{text}\n\n"
                f"Include:\n"
                f"1. Word breakdown\n"
                f"2. Grammatical structures\n"
                f"3. Key grammar rules being used"
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a Greek grammar expert. Explain Greek grammar "
                            "in a clear, educational way for language learners."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=0.5,
            )

            return response.choices[0].message.content or "Grammar explanation not available."

        except RateLimitError:
            logger.warning("OpenAI rate limit exceeded")
            return "I'm receiving too many requests right now. Please wait about a minute and try again."
        except APITimeoutError:
            logger.error("OpenAI request timeout")
            return "Your request took too long to process. Please try again with a simpler query."
        except APIConnectionError:
            logger.error("Failed to connect to OpenAI")
            return "I'm having trouble connecting to the AI service. Please check your internet connection and try again."
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return "AI service error. Please try again."
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return "Unexpected error occurred. Please try again later."

    async def generate_card_from_word(self, word: str) -> dict[str, str]:
        """Generate a flashcard from a Greek word.

        Args:
            word: Greek word

        Returns:
            Dictionary with 'front', 'back', and 'example' fields
        """
        try:
            prompt = (
                f"Create a flashcard for learning the Greek word: {word}\n\n"
                f"Provide:\n"
                f"1. The Greek word (front of card)\n"
                f"2. English translation (back of card)\n"
                f"3. An example sentence in Greek with English translation\n\n"
                f"Format your response as:\n"
                f"FRONT: [Greek word]\n"
                f"BACK: [English translation]\n"
                f"EXAMPLE: [Greek example] - [English translation]"
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a Greek language teaching expert. "
                            "Create educational flashcards for Greek vocabulary."
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
                "back": "Rate limit exceeded. Please try again later.",
                "example": "",
            }
        except APITimeoutError:
            logger.error("OpenAI request timeout")
            return {"front": word, "back": "Request timeout. Please try again.", "example": ""}
        except APIConnectionError:
            logger.error("Failed to connect to OpenAI")
            return {"front": word, "back": "Connection error. Please try again.", "example": ""}
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return {"front": word, "back": "AI service error. Please try again.", "example": ""}
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return {"front": word, "back": "", "example": ""}

    async def generate_example_sentence(self, word: str) -> str:
        """Generate an example sentence using a Greek word.

        Args:
            word: Greek word

        Returns:
            Example sentence with translation
        """
        try:
            prompt = (
                f"Create a simple example sentence in Greek using the word: {word}\n"
                f"Provide both the Greek sentence and English translation."
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Greek language teacher creating example sentences.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
                temperature=0.7,
            )

            return response.choices[0].message.content or ""

        except RateLimitError:
            logger.warning("OpenAI rate limit exceeded")
            return "Rate limit exceeded. Please try again later."
        except APITimeoutError:
            logger.error("OpenAI request timeout")
            return "Request timeout. Please try again."
        except APIConnectionError:
            logger.error("Failed to connect to OpenAI")
            return "Connection error. Please try again."
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return "AI service error. Please try again."
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return ""
