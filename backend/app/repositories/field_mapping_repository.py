"""
FieldMappingRepository — data access for FieldMapping model.

Handles field mapping-specific queries including workflow and type filtering.
"""

from __future__ import annotations

import uuid

from sqlalchemy import and_, select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.field_mapping import FieldMapping
from app.repositories.base import BaseRepository


class FieldMappingRepository(BaseRepository[FieldMapping]):
    """Repository for FieldMapping model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, FieldMapping)

    async def list_by_workflow(
        self,
        workflow_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[FieldMapping], int]:
        """List all field mappings for a workflow."""
        # Count
        count_result = await self.session.execute(
            select(func.count(FieldMapping.id)).where(
                FieldMapping.workflow_id == workflow_id
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(FieldMapping)
            .where(FieldMapping.workflow_id == workflow_id)
            .order_by(desc(FieldMapping.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        mappings = result.scalars().all()

        return mappings, total

    async def list_by_type(
        self,
        mapping_type: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[FieldMapping], int]:
        """List all field mappings of a specific type."""
        # Count
        count_result = await self.session.execute(
            select(func.count(FieldMapping.id)).where(
                FieldMapping.mapping_type == mapping_type
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(FieldMapping)
            .where(FieldMapping.mapping_type == mapping_type)
            .order_by(desc(FieldMapping.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        mappings = result.scalars().all()

        return mappings, total

    async def list_required(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[FieldMapping], int]:
        """List all required field mappings."""
        # Count
        count_result = await self.session.execute(
            select(func.count(FieldMapping.id)).where(
                FieldMapping.is_required == True
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(FieldMapping)
            .where(FieldMapping.is_required == True)
            .order_by(desc(FieldMapping.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        mappings = result.scalars().all()

        return mappings, total

    async def get_by_fields(
        self,
        workflow_id: uuid.UUID,
        portal_field: str,
        system_field: str,
    ) -> FieldMapping | None:
        """Get a field mapping by workflow and field names."""
        stmt = select(FieldMapping).where(
            and_(
                FieldMapping.workflow_id == workflow_id,
                FieldMapping.portal_field == portal_field,
                FieldMapping.system_field == system_field,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
