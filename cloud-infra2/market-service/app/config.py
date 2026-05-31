"""
IntelliWealth – Market Service Configuration
Centralized configuration management using pydantic-settings.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ---- Application ----
    APP_NAME: str = "IntelliWealth Market Intelligence Service"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # ---- Database ----
    DATABASE_URL: str = "postgresql://intelliwealth:intelliwealth_secret_2026@localhost:5432/intelliwealth_db"

    # ---- Redis ----
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300  # 5 minutes default
    REDIS_ANALYTICS_TTL: int = 600  # 10 minutes for analytics cache

    # ---- Server ----
    MARKET_SERVICE_HOST: str = "0.0.0.0"
    MARKET_SERVICE_PORT: int = 8001
    MARKET_SERVICE_LOG_LEVEL: str = "info"
    MARKET_SERVICE_CORS_ORIGINS: str = ""

    # ---- Risk Engine Thresholds ----
    RISK_HIGH_EQUITY_THRESHOLD: float = 80.0  # equity > 80% → HIGH risk
    RISK_GOLD_REDUCTION_FACTOR: float = 0.15  # gold reduces risk score by 15%
    RISK_DIVERSIFICATION_MIN_TYPES: int = 3  # minimum asset types for "diversified"

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [
            origin.strip()
            for origin in self.MARKET_SERVICE_CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
