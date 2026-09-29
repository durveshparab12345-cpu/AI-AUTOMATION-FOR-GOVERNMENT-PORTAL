"""
ExecutionRepository — data access for AutomationExecution records.

All queries are scoped to organization_id to enforce tenant isolation.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.execution import AutomationExecution, AutomationExecutionStep


class ExecutionRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, execution: AutomationExecution) -> AutomationExecution:
        self._db.add(execution)
        await self._db.commit()
        await self._db.refresh(execution)
        return execution

    async def get_by_id(
        self, execution_id: uuid.UUID, organization_id: uuid.UUID
    ) -> AutomationExecution | None:
        result = await self._db.execute(
            select(AutomationExecution)
            .options(selectinload(AutomationExecution.steps))
            .where(
                AutomationExecution.id == execution_id,
                AutomationExecution.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_org(
        self, organization_id: uuid.UUID, limit: int = 20
    ) -> list[AutomationExecution]:
        from sqlalchemy.orm import selectinload

        result = await self._db.execute(
            select(AutomationExecution)
            .options(selectinload(AutomationExecution.steps))
            .where(AutomationExecution.organization_id == organization_id)
            .order_by(AutomationExecution.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_steps(
        self, execution_id: uuid.UUID, organization_id: uuid.UUID
    ) -> list[AutomationExecutionStep]:
        # First verify org ownership
        execution = await self.get_by_id(execution_id, organization_id)
        if not execution:
            return []
        result = await self._db.execute(
            select(AutomationExecutionStep)
            .where(AutomationExecutionStep.execution_id == execution_id)
            .order_by(AutomationExecutionStep.step_number)
        )
        return list(result.scalars().all())
