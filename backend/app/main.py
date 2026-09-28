"""
FastAPI application factory.

This module creates and configures the FastAPI application instance.
It is the single entry point for Uvicorn:

    uvicorn app.main:app --reload

Responsibilities of this module:
  - Instantiate the FastAPI app with metadata.
  - Configure CORS middleware.
  - Mount versioned API routers.
  - Register startup/shutdown lifecycle hooks via the modern lifespan pattern.

Business logic must NOT live here — it belongs in services/.
Route logic must NOT live here — it belongs in api/.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import health as health_router
from app.core.config import settings
from app.core.logging import configure_logging

# Configure application-wide logging as early as possible.
configure_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.

    Code before `yield` runs on startup; code after `yield` runs on shutdown.
    Future stages can add database pool warm-up, cache priming, etc. here.
    """
    logger.info(
        "Starting %s | env=%s | debug=%s",
        settings.APP_NAME,
        settings.APP_ENV,
        settings.DEBUG,
    )
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


def create_app() -> FastAPI:
    """
    Application factory.

    Returns a fully configured FastAPI instance.  Using a factory function
    (rather than a bare module-level `app = FastAPI()`) makes the application
    easier to test — tests can call `create_app()` to get a fresh instance
    with controlled settings.
    """
    application = FastAPI(
        title=settings.APP_NAME,
        description=(
            "AI Portal Automation Platform API — "
            "Stage 1: System Foundation. "
            "Browser automation, AI reasoning, and portal integrations "
            "are not yet implemented."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # -------------------------------------------------------------------------
    # CORS middleware
    # Allow the frontend dev server to reach the API during development.
    # In production, CORS_ORIGINS should be restricted to known frontend domains.
    # -------------------------------------------------------------------------
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -------------------------------------------------------------------------
    # API routers
    # All routes are versioned under /api/v1/.
    # Future modules (auth, companies, portals, workflows, executions) will be
    # registered here in subsequent stages.
    # -------------------------------------------------------------------------
    application.include_router(
        health_router.router,
        prefix="/api/v1",
    )

    return application


# Module-level app instance used by Uvicorn.
app: FastAPI = create_app()
