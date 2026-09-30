"""
PermissionRepository — data access for Permission model.

Handles permission-specific queries like:
  - Finding permissions by resource and action
  - Listing all permissions
  - Checking permission availability
"""

from __future__ import annotations

import uuid

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.repositories.base import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    """Repository for Permission model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Permission)

    async def get_by_resource_action(
        self,
        resource: str,
        action: str,
    ) -> Permission | None:
        """Get a permission by resource and action."""
        stmt = select(Permission).where(
            and_(
                Permission.resource == resource,
                Permission.action == action,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        resource: str,
        action: str,
    ) -> Permission:
        """Get a permission or create it if it doesn't exist."""
        existing = await self.get_by_resource_action(resource, action)
        if existing:
            return existing

        # Create new permission
        new_permission = await self.create(
            {
                "resource": resource,
                "action": action,
            }
        )
        return new_permission

    async def list_by_resource(
        self,
        resource: str,
    ) -> list[Permission]:
        """List all permissions for a resource."""
        stmt = select(Permission).where(Permission.resource == resource)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_all(self) -> list[Permission]:
        """List all permissions in the system."""
        stmt = select(Permission)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_permission_matrix(self) -> dict[str, list[str]]:
        """
        Get permission matrix: resource -> list of actions.

        Useful for UI to show available permissions.
        """
        permissions = await self.list_all()
        matrix: dict[str, list[str]] = {}

        for perm in permissions:
            if perm.resource not in matrix:
                matrix[perm.resource] = []
            matrix[perm.resource].append(perm.action)

        return matrix
