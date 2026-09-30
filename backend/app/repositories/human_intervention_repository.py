"""
HumanInterventionRepository — data access for HumanIntervention model.

Handles human intervention-specific queries including status filtering and automation tracking.
"""

from __future__ import annotations

import uuid

from sqlalchemy import and_, select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.human_intervention import HumanIntervention
from app.repositories.base import BaseRepository


class HumanInterventionRepository(BaseRepository[HumanIntervention]):
    """Repository for HumanIntervention model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, HumanIntervention)

    async def list_by_status(
        self,
        status: str,
        tenant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[HumanIntervention], int]:
        """List all interventions with a specific status."""
        # Count
        count_result = await self.session.execute(
            select(func.count(HumanIntervention.id)).where(
                and_(
                    HumanIntervention.status == status,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(HumanIntervention)
            .where(HumanIntervention.status == status)
            .order_by(desc(HumanIntervention.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        interventions = result.scalars().all()

        return interventions, total

    async def list_by_automation(
        self,
        automation_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[HumanIntervention], int]:
        """List all interventions for an automation."""
        # Count
        count_result = await self.session.execute(
            select(func.count(HumanIntervention.id)).where(
                HumanIntervention.automation_id == automation_id
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(HumanIntervention)
            .where(HumanIntervention.automation_id == automation_id)
            .order_by(desc(HumanIntervention.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        interventions = result.scalars().all()

        return interventions, total

    async def list_pending(
        self,
        tenant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[HumanIntervention], int]:
        """List all pending interventions."""
        return await self.list_by_status("PENDING", tenant_id, skip, limit)
