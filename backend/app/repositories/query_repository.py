"""
QueryRepository — data access for Query model.

Handles query-related queries including status and escalation tracking.
"""

from __future__ import annotations

import uuid

from sqlalchemy import and_, select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.query import Query
from app.core.constants import QueryStatus
from app.repositories.base import BaseRepository


class QueryRepository(BaseRepository[Query]):
    """Repository for Query model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Query)

    async def list_by_case(
        self,
        case_id: uuid.UUID,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Query], int]:
        """List all queries for a case."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Query.id)).where(
                and_(
                    Query.case_id == case_id,
                    Query.tenant_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Query)
            .where(
                and_(
                    Query.case_id == case_id,
                    Query.tenant_id == organization_id,
                )
            )
            .order_by(desc(Query.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        queries = result.scalars().all()

        return queries, total

    async def list_by_status(
        self,
        status: QueryStatus,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Query], int]:
        """List all queries with a specific status."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Query.id)).where(
                and_(
                    Query.status == status,
                    Query.tenant_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Query)
            .where(
                and_(
                    Query.status == status,
                    Query.tenant_id == organization_id,
                )
            )
            .order_by(desc(Query.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        queries = result.scalars().all()

        return queries, total

    async def list_open(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Query], int]:
        """List all open queries."""
        return await self.list_by_status(QueryStatus.OPEN, organization_id, skip, limit)

    async def list_escalated(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Query], int]:
        """List all escalated queries."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Query.id)).where(
                and_(
                    Query.is_escalated == True,
                    Query.tenant_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Query)
            .where(
                and_(
                    Query.is_escalated == True,
                    Query.tenant_id == organization_id,
                )
            )
            .order_by(desc(Query.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        queries = result.scalars().all()

        return queries, total
