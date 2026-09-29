"""DemoCaseRepository — org-scoped access to demo cases."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.demo_case import DemoCase


class DemoCaseRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def list_active(self, organization_id: uuid.UUID) -> list[DemoCase]:
        result = await self._db.execute(
            select(DemoCase)
            .where(
                DemoCase.organization_id == organization_id,
                DemoCase.is_active.is_(True),
            )
            .order_by(DemoCase.case_ref)
        )
        return list(result.scalars().all())

    async def get_by_id(self, case_id: uuid.UUID, organization_id: uuid.UUID) -> DemoCase | None:
        result = await self._db.execute(
            select(DemoCase).where(
                DemoCase.id == case_id,
                DemoCase.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()
