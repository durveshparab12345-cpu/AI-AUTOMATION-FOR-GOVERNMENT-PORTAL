"""
Tests for the health check endpoint.

Verifies:
  - GET /api/v1/health returns HTTP 200
  - Response body is {"status": "healthy"}

These tests use HTTPX's AsyncClient with the ASGI transport so that
no real network socket is opened — the tests are fast and self-contained.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_returns_200() -> None:
    """GET /api/v1/health must respond with HTTP 200."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_response_body() -> None:
    """GET /api/v1/health must return {"status": "healthy"}."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get("/api/v1/health")

    data = response.json()
    assert data == {"status": "healthy"}


@pytest.mark.asyncio
async def test_health_content_type_is_json() -> None:
    """GET /api/v1/health must return a JSON content-type header."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get("/api/v1/health")

    assert "application/json" in response.headers.get("content-type", "")
