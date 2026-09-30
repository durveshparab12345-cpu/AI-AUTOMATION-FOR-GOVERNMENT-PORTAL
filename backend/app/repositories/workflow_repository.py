"""
WorkflowRepository — data access for Workflow model.

Handles workflow-specific queries including status and version filtering.
"""

from __future__ import annotations

import uuid

from sqlalchemy import and_, select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import Workflow
from app.core.constants import WorkflowStatus
from app.repositories.base import BaseRepository


class WorkflowRepository(BaseRepository[Workflow]):
    """Repository for Workflow model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Workflow)

    async def list_by_status(
        self,
        status: WorkflowStatus,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Workflow], int]:
        """List all workflows with a specific status."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Workflow.id)).where(
                and_(
                    Workflow.status == status,
                    Workflow.tenant_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Workflow)
            .where(
                and_(
                    Workflow.status == status,
                    Workflow.tenant_id == organization_id,
                )
            )
            .order_by(desc(Workflow.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        workflows = result.scalars().all()

        return workflows, total

    async def get_by_name(
        self,
        name: str,
        organization_id: uuid.UUID,
    ) -> Workflow | None:
        """Get a workflow by name."""
        stmt = select(Workflow).where(
            and_(
                Workflow.name == name,
                Workflow.tenant_id == organization_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Workflow], int]:
        """List all active workflows."""
        return await self.list_by_status(WorkflowStatus.ACTIVE, organization_id, skip, limit)

    async def list_drafts(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Workflow], int]:
        """List all draft workflows."""
        return await self.list_by_status(WorkflowStatus.DRAFT, organization_id, skip, limit)
