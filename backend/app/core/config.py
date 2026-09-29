"""
Centralized application configuration.

All settings are loaded from environment variables (or a .env file).
No secret has a safe hard-coded default for production.

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
    # Security — MUST be overridden in production
    # -------------------------------------------------------------------------
    SECRET_KEY: str = "CHANGE-ME-IN-PRODUCTION-USE-A-RANDOM-SECRET-KEY"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # -------------------------------------------------------------------------
    # Database
    # -------------------------------------------------------------------------
    DATABASE_URL: str = "postgresql+asyncpg://postgres:changeme@localhost:5432/ai_portal_dev"

    # -------------------------------------------------------------------------
    # Redis (reserved for future stages)
    # -------------------------------------------------------------------------
    REDIS_URL: str = "redis://localhost:6379/0"

    # -------------------------------------------------------------------------
    # CORS
    # -------------------------------------------------------------------------
    CORS_ORIGINS: str = "http://localhost:5173"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: str | list) -> str:
        if isinstance(value, list):
            return ",".join(value)
        return value

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # -------------------------------------------------------------------------
    # Demo / Prototype settings
    # -------------------------------------------------------------------------
    DEMO_MODE: bool = True  # seed demo data on startup

    # Screenshots — stored server-side, not publicly served
    SCREENSHOT_DIR: str = "screenshots"

    # Playwright browser visibility — False = headless, True = visible (for live demos)
    BROWSER_HEADLESS: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application Settings instance."""
    return Settings()


settings: Settings = get_settings()
