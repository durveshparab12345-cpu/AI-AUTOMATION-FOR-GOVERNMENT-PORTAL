"""
ReportRepository — data access for Report model.

Handles report-specific queries including type filtering and generation tracking.
"""

from __future__ import annotations

import uuid

from sqlalchemy import and_, select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report
from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository[Report]):
    """Repository for Report model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Report)

    async def list_by_type(
        self,
        report_type: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Report], int]:
        """List all reports of a specific type."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Report.id)).where(
                Report.report_type == report_type
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Report)
            .where(Report.report_type == report_type)
            .order_by(desc(Report.generated_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        reports = result.scalars().all()

        return reports, total

    async def list_by_scope(
        self,
        scope: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Report], int]:
        """List all reports for a specific scope."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Report.id)).where(
                Report.scope == scope
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Report)
            .where(Report.scope == scope)
            .order_by(desc(Report.generated_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        reports = result.scalars().all()

        return reports, total

    async def list_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Report], int]:
        """List all reports with a specific status."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Report.id)).where(
                Report.status == status
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Report)
            .where(Report.status == status)
            .order_by(desc(Report.generated_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        reports = result.scalars().all()

        return reports, total

    async def list_scheduled(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Report], int]:
        """List all scheduled reports."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Report.id)).where(
                Report.is_scheduled == True
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Report)
            .where(Report.is_scheduled == True)
            .order_by(desc(Report.generated_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        reports = result.scalars().all()

        return reports, total
