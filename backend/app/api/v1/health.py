"""
Health check endpoint.

GET /api/v1/health

Returns a minimal JSON payload indicating the application is running.
This endpoint is intentionally dependency-free (no database call) so that
a load balancer or container orchestrator can confirm the process is alive
even when the database is temporarily unavailable.

A richer "readiness" endpoint (which checks database connectivity, etc.)
can be added in a future stage.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Schema for the health check response."""

    status: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application health check",
    tags=["Health"],
)
async def health_check() -> HealthResponse:
    """
    Returns `{"status": "healthy"}` when the application process is running.

    This is a liveness probe — it confirms the process is alive and the
    framework is responding.  It does NOT verify external dependencies such
    as the database or Redis.
    """
    return HealthResponse(status="healthy")
