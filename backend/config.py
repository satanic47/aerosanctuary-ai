"""Configuration module for AeroSanctuary AI.

Handles environment variable loading, runtime defaults, and security configurations
using Pydantic BaseSettings for strict type enforcement and validation.
"""

from pydantic import ConfigDict, Field

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings  # Fallback compatibility


class Settings(BaseSettings):
    """Application configuration settings."""

    # Modern Pydantic V2 configuration
    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # Application Metadata
    APP_NAME: str = "AeroSanctuary AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(
        default="production",
        description="Environment mode (development/production/testing)",
    )
    DEBUG: bool = Field(default=False, description="Debug mode flag")

    # Server Configuration
    HOST: str = "127.0.0.1"  # nosec B104
    PORT: int = 8000
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "https://aerosanctuary.onrender.com",
    ]

    # Security & Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = 60
    MAX_PAYLOAD_SIZE_BYTES: int = 1048576  # 1 MB
    PROMPT_INJECTION_CHECK_ENABLED: bool = True

    # Generative AI Credentials (Optional for local deterministic fallback)
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API key for GenAI assistant")
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # AQI Data Provider
    DEFAULT_AQI_FALLBACK_CITY: str = "Delhi-NCR"
    CACHE_TTL_SECONDS: int = 900  # 15 minutes TTL for AQI & reasoning caching


# Global settings singleton
settings = Settings()
