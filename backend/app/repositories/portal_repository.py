"""
PortalRepository — data access for Portal model.

Handles portal-specific queries including status filtering and discovery.
"""

from __future__ import annotations

import uuid

from sqlalchemy import and_, select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portal import Portal
from app.core.constants import PortalStatus, PortalType
from app.repositories.base import BaseRepository


class PortalRepository(BaseRepository[Portal]):
    """Repository for Portal model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Portal)

    async def list_by_status(
        self,
        status: PortalStatus,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Portal], int]:
        """List all portals with a specific status."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Portal.id)).where(
                and_(
                    Portal.status == status,
                    Portal.tenant_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Portal)
            .where(
                and_(
                    Portal.status == status,
                    Portal.tenant_id == organization_id,
                )
            )
            .order_by(desc(Portal.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        portals = result.scalars().all()

        return portals, total

    async def list_by_type(
        self,
        portal_type: PortalType,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Portal], int]:
        """List all portals of a specific type."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Portal.id)).where(
                and_(
                    Portal.type == portal_type,
                    Portal.tenant_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Portal)
            .where(
                and_(
                    Portal.type == portal_type,
                    Portal.tenant_id == organization_id,
                )
            )
            .order_by(desc(Portal.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        portals = result.scalars().all()

        return portals, total

    async def get_by_name(
        self,
        name: str,
        organization_id: uuid.UUID,
    ) -> Portal | None:
        """Get a portal by name."""
        stmt = select(Portal).where(
            and_(
                Portal.name == name,
                Portal.tenant_id == organization_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Portal], int]:
        """List all active portals."""
        return await self.list_by_status(PortalStatus.ACTIVE, organization_id, skip, limit)
