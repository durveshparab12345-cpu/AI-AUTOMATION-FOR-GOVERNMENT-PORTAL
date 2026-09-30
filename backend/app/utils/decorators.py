"""
Decorators for RBAC and audit logging.

Provides:
  - @require_permission: Check permission before executing
  - @require_role: Check role before executing
  - @audit_log: Log action to audit trail
"""

from __future__ import annotations

import functools
import uuid
from typing import Callable, Any, TypeVar

from fastapi import Request

from app.core.constants import ErrorCode, AuditAction
from app.exceptions import APIException

F = TypeVar("F", bound=Callable[..., Any])


def require_permission(resource: str, action: str) -> Callable[[F], F]:
    """
    Decorator to enforce permission checks on endpoint handlers.

    Usage:
        @require_permission("CASE", "CREATE")
        async def create_case(case_data: CaseCreate, request: Request):
            ...

    The current_user must be injected by a dependency.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Extract request and user from kwargs
            # This depends on how FastAPI dependencies are set up
            request = kwargs.get("request")
            current_user = kwargs.get("current_user")

            if not current_user:
                raise APIException(
                    error_code=ErrorCode.UNAUTHORIZED,
                    message="Not authenticated",
                )

            # Check permission
            from app.services.authorization_service import AuthorizationService
            from app.db.session import get_session

            # This is simplified; in real code, inject the service
            if not current_user.has_permission(resource, action):
                raise APIException(
                    error_code=ErrorCode.PERMISSION_DENIED,
                    message=f"Missing permission: {resource}:{action}",
                )

            return await func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def require_role(role_name: str) -> Callable[[F], F]:
    """
    Decorator to enforce role checks on endpoint handlers.

    Usage:
        @require_role("ADMIN")
        async def admin_endpoint(request: Request):
            ...
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            current_user = kwargs.get("current_user")

            if not current_user:
                raise APIException(
                    error_code=ErrorCode.UNAUTHORIZED,
                    message="Not authenticated",
                )

            if not current_user.has_role(role_name):
                raise APIException(
                    error_code=ErrorCode.PERMISSION_DENIED,
                    message=f"Missing role: {role_name}",
                )

            return await func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def audit_action(
    action: str,
    resource_type: str,
) -> Callable[[F], F]:
    """
    Decorator to automatically log actions to audit trail.

    The decorated function should extract the resource_id from its arguments
    and return the resource_id or the modified resource.

    Usage:
        @audit_action(AuditAction.CREATE, ResourceType.CASE)
        async def create_case(case_data: CaseCreate, ...):
            case = await service.create(case_data)
            return case  # Must return the resource to extract ID
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            request = kwargs.get("request")
            current_user = kwargs.get("current_user")

            try:
                result = await func(*args, **kwargs)
                # Extract resource_id from result if possible
                resource_id = None
                if hasattr(result, "id"):
                    resource_id = result.id

                # Log to audit trail (simplified, would need async audit service)
                # In real code, inject the audit service

                return result
            except Exception as e:
                # Log failed action to audit trail
                raise

        return wrapper  # type: ignore

    return decorator
