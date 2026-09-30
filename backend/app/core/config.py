"""
Centralized application configuration with environment support.

All settings are loaded from environment variables (or a .env file).
Configuration hierarchy (highest priority first):
  1. Environment variables
  2. .env file
  3. Code defaults

CRITICAL: In production, override SECRET_KEY and other security settings.

Usage:
    from app.core.config import settings, Environment
    print(settings.APP_ENV)  # "production", "development", etc.
"""

from __future__ import annotations

import os
from enum import Enum
from functools import lru_cache
from typing import Literal

# Load .env file if exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Environment(str, Enum):
    """Application environments with different security/debug settings."""

    DEVELOPMENT = "development"
    TEST = "test"
    DEMO = "demo"
    PRODUCTION = "production"


class Settings:
    """Application settings resolved from environment variables."""

    # =========================================================================
    # APPLICATION IDENTITY & ENVIRONMENT
    # =========================================================================
    APP_NAME: str = "AI Portal Automation Platform"
    APP_ENV: Environment
    VERSION: str = "1.0.0"

    # =========================================================================
    # DEBUG & LOGGING
    # =========================================================================
    DEBUG: bool
    LOG_LEVEL: str

    # =========================================================================
    # SECURITY - CRITICAL CONFIGURATION
    # =========================================================================
    SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # Rate limiting (requests per minute)
    RATE_LIMIT_LOGIN: int
    RATE_LIMIT_API: int
    RATE_LIMIT_DOCUMENT_UPLOAD: int

    # =========================================================================
    # DATABASE CONFIGURATION
    # =========================================================================
    DATABASE_URL: str
    DATABASE_ECHO: bool
    DATABASE_POOL_SIZE: int
    DATABASE_MAX_OVERFLOW: int

    # =========================================================================
    # REDIS CONFIGURATION (caching, sessions, rate limiting)
    # =========================================================================
    REDIS_URL: str
    REDIS_ENABLED: bool

    # =========================================================================
    # CORS & SECURITY HEADERS
    # =========================================================================
    CORS_ORIGINS: str
    CORS_ALLOW_CREDENTIALS: bool
    CORS_ALLOW_METHODS: list[str]
    CORS_ALLOW_HEADERS: list[str]
    CORS_MAX_AGE: int

    # Security headers
    HSTS_MAX_AGE: int
    ENABLE_HSTS: bool

    # =========================================================================
    # BROWSER AUTOMATION (Playwright)
    # =========================================================================
    BROWSER_HEADLESS: bool
    BROWSER_TIMEOUT_MS: int
    SCREENSHOT_DIR: str
    SCREENSHOT_ON_ERROR: bool

    # =========================================================================
    # AI INTEGRATION
    # =========================================================================
    AI_PROVIDER: str
    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str
    AI_TIMEOUT_SECONDS: int

    # =========================================================================
    # PORTAL INTEGRATION
    # =========================================================================
    PMJAY_PORTAL_URL: str
    PMJAY_ENVIRONMENT: Literal["development", "staging", "production"]

    # =========================================================================
    # DOCUMENT & FILE STORAGE
    # =========================================================================
    USE_S3: bool
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET: str
    AWS_S3_REGION: str
    MAX_UPLOAD_SIZE_MB: int

    # =========================================================================
    # EMAIL & NOTIFICATIONS
    # =========================================================================
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    EMAIL_FROM: str
    EMAIL_FROM_NAME: str

    # =========================================================================
    # DEMO & PROTOTYPE MODE
    # =========================================================================
    DEMO_MODE: bool
    USE_MOCK_PORTAL: bool
    USE_MOCK_AI: bool

    # =========================================================================
    # MONITORING & OBSERVABILITY
    # =========================================================================
    ENABLE_METRICS: bool
    ENABLE_TRACING: bool
    JAEGER_ENABLED: bool
    JAEGER_AGENT_HOST: str
    JAEGER_AGENT_PORT: int

    # =========================================================================
    # FEATURE FLAGS
    # =========================================================================
    FEATURE_TEACH_MODE: bool
    FEATURE_AI_WORKFLOW_GENERATION: bool
    FEATURE_DOCUMENT_OCR: bool
    FEATURE_ADVANCED_ANALYTICS: bool

    def __init__(self):
        """Initialize settings from environment variables."""
        self.APP_ENV = Environment(os.getenv("APP_ENV", "development"))
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

        self.SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE-ME-IN-PRODUCTION-GENERATE-RANDOM-32-BYTE-KEY")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

        self.RATE_LIMIT_LOGIN = int(os.getenv("RATE_LIMIT_LOGIN", "5"))
        self.RATE_LIMIT_API = int(os.getenv("RATE_LIMIT_API", "1000"))
        self.RATE_LIMIT_DOCUMENT_UPLOAD = int(os.getenv("RATE_LIMIT_DOCUMENT_UPLOAD", "100"))

        self.DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:changeme@localhost:5432/ai_portal_dev")
        self.DATABASE_ECHO = os.getenv("DATABASE_ECHO", "false").lower() == "true"
        self.DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "10"))
        self.DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))

        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"

        self.CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173")
        self.CORS_ALLOW_CREDENTIALS = True
        self.CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE"]
        self.CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]
        self.CORS_MAX_AGE = int(os.getenv("CORS_MAX_AGE", "600"))

        self.HSTS_MAX_AGE = int(os.getenv("HSTS_MAX_AGE", "31536000"))
        self.ENABLE_HSTS = os.getenv("ENABLE_HSTS", "false").lower() == "true"

        self.BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
        self.BROWSER_TIMEOUT_MS = int(os.getenv("BROWSER_TIMEOUT_MS", "30000"))
        self.SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "screenshots")
        self.SCREENSHOT_ON_ERROR = os.getenv("SCREENSHOT_ON_ERROR", "true").lower() == "true"

        self.AI_PROVIDER = os.getenv("AI_PROVIDER", "mock")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
        self.ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-opus")
        self.AI_TIMEOUT_SECONDS = int(os.getenv("AI_TIMEOUT_SECONDS", "60"))

        self.PMJAY_PORTAL_URL = os.getenv("PMJAY_PORTAL_URL", "https://tmis.pmjay.gov.in")
        self.PMJAY_ENVIRONMENT = os.getenv("PMJAY_ENVIRONMENT", "development")

        self.USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
        self.AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
        self.AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
        self.AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "ai-portal-documents")
        self.AWS_S3_REGION = os.getenv("AWS_S3_REGION", "us-east-1")
        self.MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))

        self.SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
        self.EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@aiportal.com")
        self.EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "AI Portal")

        self.DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
        self.USE_MOCK_PORTAL = os.getenv("USE_MOCK_PORTAL", "false").lower() == "true"
        self.USE_MOCK_AI = os.getenv("USE_MOCK_AI", "false").lower() == "true"

        self.ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        self.ENABLE_TRACING = os.getenv("ENABLE_TRACING", "false").lower() == "true"
        self.JAEGER_ENABLED = os.getenv("JAEGER_ENABLED", "false").lower() == "true"
        self.JAEGER_AGENT_HOST = os.getenv("JAEGER_AGENT_HOST", "localhost")
        self.JAEGER_AGENT_PORT = int(os.getenv("JAEGER_AGENT_PORT", "6831"))

        self.FEATURE_TEACH_MODE = os.getenv("FEATURE_TEACH_MODE", "false").lower() == "true"
        self.FEATURE_AI_WORKFLOW_GENERATION = os.getenv("FEATURE_AI_WORKFLOW_GENERATION", "false").lower() == "true"
        self.FEATURE_DOCUMENT_OCR = os.getenv("FEATURE_DOCUMENT_OCR", "false").lower() == "true"
        self.FEATURE_ADVANCED_ANALYTICS = os.getenv("FEATURE_ADVANCED_ANALYTICS", "false").lower() == "true"

        # Validate on initialization
        if self.APP_ENV == Environment.PRODUCTION:
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production")
            if len(self.SECRET_KEY) < 32 or self.SECRET_KEY.startswith("CHANGE"):
                raise ValueError("SECRET_KEY must be 32+ bytes and not the default in production")
            if self.DEMO_MODE:
                raise ValueError("DEMO_MODE must be False in production")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.APP_ENV == Environment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        """Check if running in test environment."""
        return self.APP_ENV == Environment.TEST

    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic migrations."""
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")

    def get_environment_info(self) -> dict:
        """Get environment information for logging/monitoring."""
        return {
            "app_name": self.APP_NAME,
            "app_version": self.VERSION,
            "environment": self.APP_ENV.value,
            "debug": self.DEBUG,
            "database": "postgresql",
            "redis": "enabled" if self.REDIS_ENABLED else "disabled",
            "ai_provider": self.AI_PROVIDER,
            "demo_mode": self.DEMO_MODE,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application Settings instance."""
    settings = Settings()
    # Validate on startup
    if settings.is_production:
        assert not settings.DEBUG, "DEBUG must be False in production"
        assert len(settings.SECRET_KEY) >= 32, "SECRET_KEY must be 32+ bytes"
        assert not settings.DEMO_MODE, "DEMO_MODE must be False in production"
    return settings


settings: Settings = get_settings()
