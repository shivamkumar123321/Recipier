"""
Application configuration settings.

Uses Pydantic Settings for environment variable management.
"""

from typing import Any, Dict, List, Optional

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables are loaded from .env file in development.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    # Application
    PROJECT_NAME: str = "Weight Coach"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/weight_coach",
        description="Async PostgreSQL database URL",
    )
    DATABASE_POOL_SIZE: int = Field(default=5)

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for caching",
    )

    # JWT Authentication
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production-use-openssl-rand-hex-32",
        description="Secret key for JWT token generation",
    )
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # OpenAI API
    OPENAI_API_KEY: str = Field(
        default="",
        description="OpenAI API key for GPT-4, Whisper, Vision",
    )
    OPENAI_MODEL: str = Field(
        default="gpt-4",
        description="Default GPT model (gpt-4, gpt-4-turbo, gpt-3.5-turbo)",
    )
    OPENAI_MAX_TOKENS: int = Field(
        default=1000,
        description="Maximum tokens for completions",
    )
    OPENAI_TEMPERATURE: float = Field(
        default=0.7,
        description="Temperature for text generation (0.0-2.0)",
    )

    # OpenAI Advanced Settings
    OPENAI_VISION_MODEL: str = Field(
        default="gpt-4-vision-preview",
        description="Model for vision tasks",
    )
    OPENAI_MAX_RETRIES: int = Field(
        default=3,
        description="Maximum number of retries for failed requests",
    )
    OPENAI_TIMEOUT: int = Field(
        default=60,
        description="Request timeout in seconds",
    )
    OPENAI_CACHE_TTL: int = Field(
        default=3600,
        description="Cache TTL in seconds for repeated queries (1 hour default)",
    )
    OPENAI_ENABLE_CACHING: bool = Field(
        default=True,
        description="Enable Redis caching for OpenAI responses",
    )
    OPENAI_TRACK_USAGE: bool = Field(
        default=True,
        description="Track token usage for cost monitoring",
    )

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins",
    )

    # Frontend URL
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Frontend application URL for email links",
    )

    # Email (SendGrid)
    SENDGRID_API_KEY: Optional[str] = Field(
        default=None,
        description="SendGrid API key for production emails",
    )
    FROM_EMAIL: str = Field(
        default="noreply@weightcoach.app",
        description="From email address for outgoing emails",
    )

    # API Settings
    API_V1_PREFIX: str = "/api/v1"

    # File Upload
    MAX_UPLOAD_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum file upload size in bytes",
    )
    ALLOWED_IMAGE_TYPES: List[str] = Field(
        default=["image/jpeg", "image/png", "image/webp"],
    )

    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=20)
    MAX_PAGE_SIZE: int = Field(default=100)

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            # Handle JSON string or comma-separated string
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v


# Create global settings instance
settings = Settings()
