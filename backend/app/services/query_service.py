"""
QueryService — manage queries and clarifications during case processing.
"""

from __future__ import annotations

import uuid
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.query import Query
from app.repositories.query_repository import QueryRepository
from app.core.constants import QueryStatus, ErrorCode
from app.exceptions import APIException

logger = logging.getLogger(__name__)


class QueryService:
    """Service for query management."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session
        self.query_repo = QueryRepository(session)

    async def create_query(
        self,
        organization_id: uuid.UUID,
        case_id: uuid.UUID | None,
        automation_id: uuid.UUID | None,
        title: str,
        description: str,
        created_by: uuid.UUID | None = None,
    ) -> Query:
        """Create a new query."""
        query = await self.query_repo.create(
            {
                "tenant_id": organization_id,
                "case_id": case_id,
                "automation_id": automation_id,
                "title": title,
                "description": description,
                "status": QueryStatus.OPEN,
                "created_by": created_by,
            },
        )

        await self.session.commit()
        logger.info(f"Query created: {query.id} ({title})")
        return query

    async def get_query(
        self,
        query_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Query:
        """Get query by ID."""
        query = await self.query_repo.read(query_id, organization_id)
        if not query:
            raise APIException(
                error_code=ErrorCode.NOT_FOUND,
                message="Query not found",
            )
        return query

    async def respond_to_query(
        self,
        query_id: uuid.UUID,
        organization_id: uuid.UUID,
        response: str,
        response_from: str | None = None,
    ) -> Query:
        """Add response to a query."""
        query = await self.get_query(query_id, organization_id)

        query = await self.query_repo.update(
            query_id,
            {
                "status": QueryStatus.RESPONDED,
                "response": response,
                "response_date": datetime.now(timezone.utc),
                "response_from": response_from,
            },
            organization_id,
        )

        await self.session.commit()
        logger.info(f"Query responded: {query_id}")
        return query

    async def resolve_query(
        self,
        query_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Query:
        """Mark query as resolved."""
        query = await self.get_query(query_id, organization_id)

        query = await self.query_repo.update(
            query_id,
            {"status": QueryStatus.RESOLVED},
            organization_id,
        )

        await self.session.commit()
        logger.info(f"Query resolved: {query_id}")
        return query

    async def escalate_query(
        self,
        query_id: uuid.UUID,
        organization_id: uuid.UUID,
        reason: str,
    ) -> Query:
        """Escalate a query."""
        query = await self.get_query(query_id, organization_id)

        query = await self.query_repo.update(
            query_id,
            {"is_escalated": True, "escalation_reason": reason},
            organization_id,
        )

        await self.session.commit()
        logger.info(f"Query escalated: {query_id}")
        return query

    async def list_open_queries(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Query], int]:
        """List all open queries."""
        return await self.query_repo.list_open(organization_id, skip, limit)

    async def list_case_queries(
        self,
        case_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> list[Query]:
        """List all queries for a case."""
        queries, _ = await self.query_repo.list_by_case(
            case_id,
            organization_id,
            skip=0,
            limit=1000,
        )
        return queries
