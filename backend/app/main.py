"""
FastAPI application factory — Stage 2A: PM-JAY Live Prototype.

Registers all API routers and manages application lifecycle:
  - Startup: seeding demo data, initializing BrowserManager and WorkflowRunner
  - Shutdown: closing all open browser sessions

Business logic lives in services/.
Route logic lives in api/.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth as auth_router
from app.api.v1 import health as health_router
from app.api.v1 import pmjay_demo as pmjay_router
from app.api.v1 import portals as portals_router
from app.api.v1 import workflows as workflows_router
from app.api.v1 import automations as automations_router
from app.api.v1 import human_interventions as human_interventions_router
from app.api.v1 import exceptions as exceptions_router
from app.api.v1 import notifications as notifications_router
from app.api.v1 import reports as reports_router
from app.api.v1 import field_mappings as field_mappings_router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown lifecycle."""
    from app.db.session import AsyncSessionLocal
    from app.services.browser.browser_manager import BrowserManager
    from app.services.workflow_runner import WorkflowRunner

    logger.info(
        "Starting %s | env=%s | debug=%s | demo_mode=%s",
        settings.APP_NAME,
        settings.APP_ENV,
        settings.DEBUG,
        settings.DEMO_MODE,
    )

    # Attach BrowserManager and WorkflowRunner to app state
    application.state.browser_manager = BrowserManager()
    application.state.workflow_runner = WorkflowRunner(
        browser_manager=application.state.browser_manager
    )

    # Seed demo data if DEMO_MODE is enabled
    if settings.DEMO_MODE:
        from app.services.demo_seeder import seed_demo_data

        try:
            async with AsyncSessionLocal() as db:
                await seed_demo_data(db)
        except Exception as exc:
            # Don't crash on seed failure — database may not be ready yet
            logger.warning("Demo data seeding failed (DB may not be ready): %s", exc)

    yield

    # Shutdown — close all open browser sessions
    logger.info("Shutting down — closing browser sessions...")
    await application.state.browser_manager.close_all()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """Application factory — returns a fully configured FastAPI instance."""
    application = FastAPI(
        title=settings.APP_NAME,
        description=(
            "AI Portal Automation Platform API — Stage 2A: PM-JAY Live Prototype. "
            "Authorized portal workflow automation with human-in-the-loop control."
        ),
        version="0.2.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    application.include_router(health_router.router, prefix="/api/v1")
    application.include_router(auth_router.router, prefix="/api/v1")
    application.include_router(pmjay_router.router, prefix="/api/v1")
    application.include_router(portals_router.router, prefix="/api/v1")
    application.include_router(workflows_router.router, prefix="/api/v1")
    application.include_router(automations_router.router, prefix="/api/v1")
    application.include_router(human_interventions_router.router, prefix="/api/v1")
    application.include_router(exceptions_router.router, prefix="/api/v1")
    application.include_router(notifications_router.router, prefix="/api/v1")
    application.include_router(reports_router.router, prefix="/api/v1")
    application.include_router(field_mappings_router.router, prefix="/api/v1")

    return application


app: FastAPI = create_app()
