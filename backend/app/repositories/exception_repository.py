"""
ExceptionRepository — data access for Exception model.

Handles exception-specific queries including error code filtering and status tracking.
"""

from __future__ import annotations

import uuid

from sqlalchemy import and_, select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exception import Exception as ExceptionModel
from app.repositories.base import BaseRepository


class ExceptionRepository(BaseRepository[ExceptionModel]):
    """Repository for Exception model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ExceptionModel)

    async def list_by_error_code(
        self,
        error_code: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ExceptionModel], int]:
        """List all exceptions with a specific error code."""
        # Count
        count_result = await self.session.execute(
            select(func.count(ExceptionModel.id)).where(
                ExceptionModel.error_code == error_code
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(ExceptionModel)
            .where(ExceptionModel.error_code == error_code)
            .order_by(desc(ExceptionModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        exceptions = result.scalars().all()

        return exceptions, total

    async def list_by_automation(
        self,
        automation_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ExceptionModel], int]:
        """List all exceptions for an automation."""
        # Count
        count_result = await self.session.execute(
            select(func.count(ExceptionModel.id)).where(
                ExceptionModel.automation_id == automation_id
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(ExceptionModel)
            .where(ExceptionModel.automation_id == automation_id)
            .order_by(desc(ExceptionModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        exceptions = result.scalars().all()

        return exceptions, total

    async def list_by_status(
        self,
        resolution_status: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ExceptionModel], int]:
        """List all exceptions with a specific resolution status."""
        # Count
        count_result = await self.session.execute(
            select(func.count(ExceptionModel.id)).where(
                ExceptionModel.resolution_status == resolution_status
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(ExceptionModel)
            .where(ExceptionModel.resolution_status == resolution_status)
            .order_by(desc(ExceptionModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        exceptions = result.scalars().all()

        return exceptions, total

    async def list_unresolved(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ExceptionModel], int]:
        """List all unresolved exceptions."""
        return await self.list_by_status("PENDING", skip, limit)
