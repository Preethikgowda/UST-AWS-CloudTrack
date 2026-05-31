"""
IntelliWealth – Portfolio Service Configuration
Centralized configuration management using pydantic-settings.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ---- Application ----
    APP_NAME: str = "IntelliWealth Portfolio Service"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # ---- Database ----
    DATABASE_URL: str = "postgresql://intelliwealth:intelliwealth_secret_2026@localhost:5432/intelliwealth_db"

    # ---- JWT ----
    JWT_SECRET_KEY: str = "change-me-to-a-secure-random-string-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ---- Server ----
    PORTFOLIO_SERVICE_HOST: str = "0.0.0.0"
    PORTFOLIO_SERVICE_PORT: int = 8000
    PORTFOLIO_SERVICE_LOG_LEVEL: str = "info"
    PORTFOLIO_SERVICE_CORS_ORIGINS: str = ""

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [
            origin.strip()
            for origin in self.PORTFOLIO_SERVICE_CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
