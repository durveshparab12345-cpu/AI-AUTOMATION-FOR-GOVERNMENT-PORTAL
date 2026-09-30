"""
RoleRepository — data access for Role model.

Handles role-specific queries like:
  - Finding roles by name
  - Loading role permissions
  - Checking role availability
"""

from __future__ import annotations

import uuid

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Repository for Role model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Role)

    async def get_by_name(
        self,
        name: str,
        organization_id: uuid.UUID,
    ) -> Role | None:
        """Get a role by name within an organization."""
        stmt = (
            select(Role)
            .where(
                and_(
                    Role.name == name,
                    Role.organization_id == organization_id,
                )
            )
            .options(selectinload(Role.permissions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_permissions(
        self,
        id: uuid.UUID,
        organization_id: uuid.UUID | None = None,
    ) -> Role | None:
        """Get a role with all its permissions eagerly loaded."""
        stmt = select(Role).where(Role.id == id).options(selectinload(Role.permissions))

        if organization_id:
            stmt = stmt.where(Role.organization_id == organization_id)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_with_permissions(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Role], int]:
        """List all roles with permissions for an organization."""
        # Count
        count_stmt = select(Role).where(Role.organization_id == organization_id)
        count_result = await self.session.execute(
            select(func.count(Role.id)).where(Role.organization_id == organization_id)
        )
        total = count_result.scalar() or 0

        # List with eager loading
        stmt = (
            select(Role)
            .where(Role.organization_id == organization_id)
            .options(selectinload(Role.permissions))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        roles = result.scalars().unique().all()

        return roles, total

    async def list_system_roles(self) -> list[Role]:
        """Get all system-defined roles."""
        stmt = select(Role).where(Role.is_system == True).options(selectinload(Role.permissions))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def is_name_available(
        self,
        name: str,
        organization_id: uuid.UUID,
        exclude_id: uuid.UUID | None = None,
    ) -> bool:
        """Check if a role name is available in an organization."""
        stmt = select(Role).where(
            and_(
                Role.name == name,
                Role.organization_id == organization_id,
            )
        )
        if exclude_id:
            stmt = stmt.where(Role.id != exclude_id)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is None
