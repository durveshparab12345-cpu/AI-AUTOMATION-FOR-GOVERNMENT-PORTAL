"""
RoleService — role and permission management.

Handles:
  - Creating and managing roles
  - Assigning permissions to roles
  - Assigning roles to users
  - Permission validation
"""

from __future__ import annotations

import uuid

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ErrorCode, RoleName, DEFAULT_SYSTEM_ROLES
from app.exceptions import APIException
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole
from app.repositories.role_repository import RoleRepository
from app.repositories.permission_repository import PermissionRepository


class RoleService:
    """Service for role management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.role_repo = RoleRepository(session)
        self.perm_repo = PermissionRepository(session)

    async def create_role(
        self,
        organization_id: uuid.UUID,
        name: str,
        description: str | None = None,
        is_system: bool = False,
    ) -> Role:
        """Create a new role."""
        # Check name is available
        is_available = await self.role_repo.is_name_available(name, organization_id)
        if not is_available:
            raise APIException(
                error_code=ErrorCode.ALREADY_EXISTS,
                message=f"Role '{name}' already exists in this organization",
            )

        role = await self.role_repo.create(
            {
                "organization_id": organization_id,
                "name": name,
                "description": description,
                "is_system": is_system,
                "is_active": True,
            }
        )
        await self.session.commit()
        return role

    async def get_role(
        self,
        role_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Role:
        """Get a role with all permissions loaded."""
        role = await self.role_repo.get_with_permissions(role_id, organization_id)
        if not role:
            raise APIException(
                error_code=ErrorCode.NOT_FOUND,
                message="Role not found",
            )
        return role

    async def list_roles(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Role], int]:
        """List all roles for an organization."""
        return await self.role_repo.list_with_permissions(organization_id, skip, limit)

    async def grant_permission(
        self,
        role_id: uuid.UUID,
        resource: str,
        action: str,
        organization_id: uuid.UUID | None = None,
    ) -> None:
        """Grant a permission to a role."""
        # Verify role exists
        role = await self.role_repo.get_with_permissions(role_id, organization_id)
        if not role:
            raise APIException(
                error_code=ErrorCode.NOT_FOUND,
                message="Role not found",
            )

        # Prevent modifying system roles
        if role.is_system:
            raise APIException(
                error_code=ErrorCode.OPERATION_NOT_PERMITTED,
                message="Cannot modify system roles",
            )

        # Get or create permission
        permission = await self.perm_repo.get_or_create(resource, action)

        # Check if already granted
        existing = await self.session.execute(
            select(RolePermission).where(
                and_(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == permission.id,
                )
            )
        )
        if existing.scalar_one_or_none():
            return  # Already granted

        # Grant permission
        role_perm = RolePermission(role_id=role_id, permission_id=permission.id)
        self.session.add(role_perm)
        await self.session.commit()

    async def revoke_permission(
        self,
        role_id: uuid.UUID,
        resource: str,
        action: str,
        organization_id: uuid.UUID | None = None,
    ) -> None:
        """Revoke a permission from a role."""
        # Verify role exists
        role = await self.role_repo.get_with_permissions(role_id, organization_id)
        if not role:
            raise APIException(
                error_code=ErrorCode.NOT_FOUND,
                message="Role not found",
            )

        # Prevent modifying system roles
        if role.is_system:
            raise APIException(
                error_code=ErrorCode.OPERATION_NOT_PERMITTED,
                message="Cannot modify system roles",
            )

        # Get permission
        permission = await self.perm_repo.get_by_resource_action(resource, action)
        if not permission:
            return  # Permission doesn't exist, nothing to revoke

        # Revoke
        await self.session.execute(
            select(RolePermission)
            .where(
                and_(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == permission.id,
                )
            )
        )
        result = await self.session.execute(
            select(RolePermission).where(
                and_(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == permission.id,
                )
            )
        )
        role_perm = result.scalar_one_or_none()
        if role_perm:
            await self.session.delete(role_perm)
            await self.session.commit()

    async def seed_system_roles(
        self,
        organization_id: uuid.UUID,
    ) -> None:
        """Create system roles for an organization."""
        for role_name in DEFAULT_SYSTEM_ROLES:
            existing = await self.role_repo.get_by_name(role_name.value, organization_id)
            if not existing:
                await self.create_role(
                    organization_id,
                    role_name.value,
                    description=f"System role: {role_name.value}",
                    is_system=True,
                )
