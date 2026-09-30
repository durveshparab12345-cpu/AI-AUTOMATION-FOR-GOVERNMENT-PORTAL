"""
AutomationStepRepository — data access for AutomationStep model.

Handles step-level execution queries for auditing and debugging.
"""

from __future__ import annotations

import uuid

from sqlalchemy import and_, select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.automation_step import AutomationStep
from app.core.constants import StepStatus
from app.repositories.base import BaseRepository


class AutomationStepRepository(BaseRepository[AutomationStep]):
    """Repository for AutomationStep model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, AutomationStep)

    async def list_by_automation(
        self,
        automation_id: uuid.UUID,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[AutomationStep], int]:
        """List all steps for an automation."""
        # Count
        count_result = await self.session.execute(
            select(func.count(AutomationStep.id)).where(
                and_(
                    AutomationStep.automation_id == automation_id,
                    AutomationStep.tenant_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(AutomationStep)
            .where(
                and_(
                    AutomationStep.automation_id == automation_id,
                    AutomationStep.tenant_id == organization_id,
                )
            )
            .order_by(AutomationStep.step_number)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        steps = result.scalars().all()

        return steps, total

    async def list_by_status(
        self,
        status: StepStatus,
        automation_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> list[AutomationStep]:
        """List all steps with a specific status for an automation."""
        stmt = (
            select(AutomationStep)
            .where(
                and_(
                    AutomationStep.status == status,
                    AutomationStep.automation_id == automation_id,
                    AutomationStep.tenant_id == organization_id,
                )
            )
            .order_by(AutomationStep.step_number)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_failed_steps(
        self,
        automation_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> list[AutomationStep]:
        """Get all failed steps for an automation."""
        return await self.list_by_status(StepStatus.FAILED, automation_id, organization_id)
