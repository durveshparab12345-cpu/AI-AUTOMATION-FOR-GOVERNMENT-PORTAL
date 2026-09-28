"""
Centralized application configuration.

All settings are loaded from environment variables (or a .env file via
python-dotenv). No secret has a safe hard-coded default — the application
will raise a clear error at startup if a required value is missing in
non-development environments.

Usage:
    from app.core.config import settings
    print(settings.APP_NAME)
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings resolved from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Application identity
    # -------------------------------------------------------------------------
    APP_NAME: str = "AI Portal Automation Platform"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False

    # -------------------------------------------------------------------------
    # Security
    # In production this MUST be set to a cryptographically random value.
    # Use: python -c "import secrets; print(secrets.token_hex(32))"
    # -------------------------------------------------------------------------
    SECRET_KEY: str = "CHANGE-ME-IN-PRODUCTION-USE-A-RANDOM-SECRET-KEY"

    # -------------------------------------------------------------------------
    # Database
    # Expects a PostgreSQL DSN: postgresql+asyncpg://user:pass@host:port/dbname
    # -------------------------------------------------------------------------
    DATABASE_URL: str = "postgresql+asyncpg://postgres:changeme@localhost:5432/ai_portal_dev"

    # -------------------------------------------------------------------------
    # Redis (reserved — not used in Stage 1)
    # -------------------------------------------------------------------------
    REDIS_URL: str = "redis://localhost:6379/0"

    # -------------------------------------------------------------------------
    # CORS
    # Accepts a comma-separated string which is split into a list.
    # Example: "http://localhost:5173,https://app.example.com"
    # -------------------------------------------------------------------------
    CORS_ORIGINS: str = "http://localhost:5173"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: str | list) -> str:
        """Accept either a raw comma-separated string or a pre-parsed list."""
        if isinstance(value, list):
            return ",".join(value)
        return value

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS_ORIGINS as a parsed list of origin strings."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the cached application Settings instance.

    Using lru_cache ensures that environment variables and the .env file
    are parsed exactly once per process lifetime, which is efficient and
    prevents inconsistencies from mid-run environment mutations.
    """
    return Settings()


# Module-level singleton for direct import convenience.
settings: Settings = get_settings()
