"""
AutomationRepository — data access for Automation model.

Handles automation execution queries including status, workflow, and case filtering.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from sqlalchemy import and_, select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.automation import Automation
from app.core.constants import ExecutionStatus
from app.repositories.base import BaseRepository


class AutomationRepository(BaseRepository[Automation]):
    """Repository for Automation model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Automation)

    async def list_by_status(
        self,
        status: ExecutionStatus,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Automation], int]:
        """List all automations with a specific status."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Automation.id)).where(
                and_(
                    Automation.status == status,
                    Automation.tenant_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Automation)
            .where(
                and_(
                    Automation.status == status,
                    Automation.tenant_id == organization_id,
                )
            )
            .order_by(desc(Automation.started_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        automations = result.scalars().all()

        return automations, total

    async def list_by_workflow(
        self,
        workflow_id: uuid.UUID,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Automation], int]:
        """List all automations for a specific workflow."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Automation.id)).where(
                and_(
                    Automation.workflow_id == workflow_id,
                    Automation.tenant_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Automation)
            .where(
                and_(
                    Automation.workflow_id == workflow_id,
                    Automation.tenant_id == organization_id,
                )
            )
            .order_by(desc(Automation.started_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        automations = result.scalars().all()

        return automations, total

    async def list_by_case(
        self,
        case_id: uuid.UUID,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Automation], int]:
        """List all automations for a specific case."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Automation.id)).where(
                and_(
                    Automation.case_id == case_id,
                    Automation.tenant_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Automation)
            .where(
                and_(
                    Automation.case_id == case_id,
                    Automation.tenant_id == organization_id,
                )
            )
            .order_by(desc(Automation.started_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        automations = result.scalars().all()

        return automations, total

    async def list_waiting_for_human(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Automation], int]:
        """List all automations waiting for human intervention."""
        return await self.list_by_status(
            ExecutionStatus.WAITING_FOR_HUMAN,
            organization_id,
            skip,
            limit,
        )

    async def list_recent(
        self,
        organization_id: uuid.UUID,
        hours: int = 24,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Automation], int]:
        """List recent automations from last N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Count
        count_result = await self.session.execute(
            select(func.count(Automation.id)).where(
                and_(
                    Automation.tenant_id == organization_id,
                    Automation.created_at >= cutoff,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Automation)
            .where(
                and_(
                    Automation.tenant_id == organization_id,
                    Automation.created_at >= cutoff,
                )
            )
            .order_by(desc(Automation.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        automations = result.scalars().all()

        return automations, total
