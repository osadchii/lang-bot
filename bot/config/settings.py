"""Application configuration using Pydantic Settings."""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Telegram Bot Configuration
    telegram_bot_token: str = Field(
        ...,
        description="Telegram Bot API token from @BotFather",
    )

    # Database Configuration
    database_url: str = Field(
        ...,
        description="PostgreSQL database URL (postgresql+asyncpg://user:pass@host:port/db)",
    )

    # OpenAI API Configuration
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key for GPT integration",
    )
    openai_model: str = Field(
        default="gpt-4",
        description="OpenAI model to use (gpt-4, gpt-4-turbo, gpt-3.5-turbo)",
    )
    openai_max_tokens: int = Field(
        default=1000,
        description="Maximum tokens for OpenAI responses",
    )
    openai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for OpenAI responses (0.0-2.0)",
    )
    openai_timeout: float = Field(
        default=30.0,
        ge=5.0,
        le=300.0,
        description="OpenAI API request timeout in seconds",
    )
    openai_vision_model: str = Field(
        default="gpt-4o",
        description="OpenAI model for vision tasks (must support vision)",
    )
    max_image_size_mb: float = Field(
        default=20.0,
        ge=1.0,
        le=20.0,
        description="Maximum image size in MB for processing",
    )

    # Application Settings
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # Database Connection Pool Settings
    db_pool_size: int = Field(
        default=10,
        ge=1,
        description="Database connection pool size",
    )
    db_max_overflow: int = Field(
        default=20,
        ge=0,
        description="Maximum overflow for database connection pool",
    )
    db_pool_timeout: int = Field(
        default=30,
        ge=1,
        description="Database connection pool timeout in seconds",
    )

    # Bot Behavior Settings
    cards_per_session: int = Field(
        default=20,
        ge=1,
        description="Default number of cards per learning session",
    )
    throttle_time: float = Field(
        default=0.5,
        ge=0.0,
        description="Throttle time between user requests in seconds",
    )

    # Conversation History Settings
    conversation_history_limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of recent messages to pass to AI for context",
    )
    conversation_retention_days: int = Field(
        default=30,
        ge=1,
        description="Number of days to retain conversation history",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the standard levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper


# Global settings instance
settings = Settings()
