"""
AuthorizationService — RBAC permission checking.

Checks if users have specific permissions through their roles.
Enforces multi-tenancy: users can only access resources in their organization.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ErrorCode, ResourceType, ActionType
from app.exceptions import APIException
from app.models.user import User
from app.repositories.role_repository import RoleRepository


class AuthorizationService:
    """Service for checking user permissions."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.role_repo = RoleRepository(session)

    async def check_permission(
        self,
        user: User,
        resource: str,
        action: str,
        organization_id: uuid.UUID | None = None,
    ) -> bool:
        """
        Check if a user has a specific permission.

        Args:
            user: The user to check
            resource: Resource type (e.g., "CASE", "USER")
            action: Action type (e.g., "CREATE", "DELETE")
            organization_id: Organization to check (for multi-tenancy)

        Returns:
            True if user has permission, False otherwise
        """
        # Super admin bypass (is_admin flag)
        if user.is_admin:
            return True

        # Check through user's roles
        return user.has_permission(resource, action)

    async def require_permission(
        self,
        user: User,
        resource: str,
        action: str,
        organization_id: uuid.UUID | None = None,
    ) -> None:
        """
        Check if a user has a specific permission or raise exception.

        Args:
            user: The user to check
            resource: Resource type
            action: Action type
            organization_id: Organization to check

        Raises:
            APIException: If user lacks permission
        """
        has_perm = await self.check_permission(user, resource, action, organization_id)
        if not has_perm:
            raise APIException(
                error_code=ErrorCode.PERMISSION_DENIED,
                message=f"User lacks permission: {resource}:{action}",
            )

    def get_user_permissions(self, user: User) -> set[str]:
        """Get all permissions a user has as resource:action strings."""
        return user.get_permissions()

    async def check_role(
        self,
        user: User,
        role_name: str,
    ) -> bool:
        """Check if a user has a specific role by name."""
        return user.has_role(role_name)

    async def require_role(
        self,
        user: User,
        role_name: str,
    ) -> None:
        """Check if a user has a specific role or raise exception."""
        has_role = await self.check_role(user, role_name)
        if not has_role:
            raise APIException(
                error_code=ErrorCode.PERMISSION_DENIED,
                message=f"User lacks required role: {role_name}",
            )

    async def check_resource_ownership(
        self,
        user: User,
        resource_type: str,
        resource_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> bool:
        """
        Check if a user can access a specific resource (multi-tenancy check).

        In future, can expand to include row-level security checks.
        Currently just verifies the resource belongs to the user's organization.
        """
        # User must belong to the same organization as the resource
        if user.organization_id != organization_id:
            return False

        return True
