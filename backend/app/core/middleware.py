"""
Application middleware components.

This module provides middleware for:
- Tenant context extraction and validation
- Request ID tracking for distributed tracing
- Rate limiting enforcement
- CORS handling
- Security headers
"""

import uuid
import time
import logging
from typing import Callable, Any
from contextvars import ContextVar

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

# Context variables for request scope
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
tenant_id_var: ContextVar[str] = ContextVar("tenant_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request IDs for distributed tracing.

    Adds a unique request ID to each request and propagates it through
    the entire request lifecycle for logging and debugging purposes.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add request ID.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            The HTTP response with request ID header
        """
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_var.set(request_id)

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        return response


class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and validate tenant context.

    Ensures that all requests are associated with a valid tenant and
    stores the tenant context for use throughout the request lifecycle.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and extract tenant context.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            The HTTP response

        Raises:
            HTTPException: If tenant validation fails
        """
        # TODO: Extract tenant_id from JWT token or header
        # TODO: Validate tenant_id against database
        # TODO: Set tenant_id_var context

        request_id = request_id_var.get()
        logger.debug(f"[{request_id}] Processing request with tenant context")

        response = await call_next(request)
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limiting.

    Implements rate limiting to prevent abuse and ensure fair resource usage
    across all clients.
    """

    def __init__(self, app: ASGIApp):
        """
        Initialize rate limit middleware.

        Args:
            app: The ASGI application
        """
        super().__init__(app)
        self.requests: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and check rate limits.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            The HTTP response or 429 Too Many Requests

        Raises:
            HTTPException: If rate limit is exceeded
        """
        # TODO: Extract client identifier (IP, user ID, API key)
        # TODO: Check rate limit using Redis or in-memory store
        # TODO: Return 429 if limit exceeded

        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to responses.

    Adds industry-standard security headers to all responses to protect
    against common web vulnerabilities.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add security headers to response.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            The HTTP response with security headers
        """
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests and responses.

    Provides comprehensive logging of request/response details including
    method, path, status code, and response time.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            The HTTP response
        """
        start_time = time.time()
        request_id = request_id_var.get()

        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - Started"
        )

        response = await call_next(request)

        process_time = time.time() - start_time
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Completed with status {response.status_code} in {process_time:.2f}s"
        )

        response.headers["X-Process-Time"] = str(process_time)
        return response


def get_request_id() -> str:
    """
    Get the current request ID from context.

    Returns:
        The request ID string
    """
    return request_id_var.get()


def get_tenant_id() -> str:
    """
    Get the current tenant ID from context.

    Returns:
        The tenant ID string
    """
    return tenant_id_var.get()


def get_user_id() -> str:
    """
    Get the current user ID from context.

    Returns:
        The user ID string
    """
    return user_id_var.get()


def set_request_id(request_id: str) -> None:
    """
    Set the request ID in context.

    Args:
        request_id: The request ID to set
    """
    request_id_var.set(request_id)


def set_tenant_id(tenant_id: str) -> None:
    """
    Set the tenant ID in context.

    Args:
        tenant_id: The tenant ID to set
    """
    tenant_id_var.set(tenant_id)


def set_user_id(user_id: str) -> None:
    """
    Set the user ID in context.

    Args:
        user_id: The user ID to set
    """
    user_id_var.set(user_id)
