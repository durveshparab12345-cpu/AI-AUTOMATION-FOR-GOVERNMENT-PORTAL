"""
BaseRepository — generic CRUD operations for all models.

Provides:
  - create(), read(), update(), delete()
  - list with filtering, pagination, sorting
  - multi-tenancy enforcement (tenant_id in all queries)
  - error handling and type safety
"""

from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.constants import ErrorCode
from app.exceptions import APIException

T = TypeVar("T", bound=DeclarativeBase)


class BaseRepository(Generic[T]):
    """Generic repository with CRUD operations."""

    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model

    async def create(
        self,
        obj_in: dict[str, Any],
        organization_id: uuid.UUID | None = None,
    ) -> T:
        """Create a new record."""
        # Auto-add organization_id if the model has it
        if organization_id and hasattr(self.model, "organization_id"):
            obj_in["organization_id"] = organization_id

        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        try:
            await self.session.flush()
        except Exception as e:
            await self.session.rollback()
            raise APIException(
                error_code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to create {self.model.__name__}",
            ) from e

        return db_obj

    async def read(
        self,
        id: uuid.UUID,
        organization_id: uuid.UUID | None = None,
    ) -> T | None:
        """Read a record by ID with multi-tenancy check."""
        filters = [self.model.id == id]

        if organization_id and hasattr(self.model, "organization_id"):
            filters.append(self.model.organization_id == organization_id)

        stmt = select(self.model).where(and_(*filters))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_by_field(
        self,
        field_name: str,
        field_value: Any,
        organization_id: uuid.UUID | None = None,
    ) -> T | None:
        """Read a record by a specific field."""
        filters = [getattr(self.model, field_name) == field_value]

        if organization_id and hasattr(self.model, "organization_id"):
            filters.append(self.model.organization_id == organization_id)

        stmt = select(self.model).where(and_(*filters))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(
        self,
        id: uuid.UUID,
        obj_in: dict[str, Any],
        organization_id: uuid.UUID | None = None,
    ) -> T | None:
        """Update a record."""
        db_obj = await self.read(id, organization_id)
        if not db_obj:
            return None

        # Update fields
        for key, value in obj_in.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)

        try:
            await self.session.flush()
        except Exception as e:
            await self.session.rollback()
            raise APIException(
                error_code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to update {self.model.__name__}",
            ) from e

        return db_obj

    async def delete(
        self,
        id: uuid.UUID,
        organization_id: uuid.UUID | None = None,
    ) -> bool:
        """Delete a record."""
        db_obj = await self.read(id, organization_id)
        if not db_obj:
            return False

        try:
            await self.session.delete(db_obj)
            await self.session.flush()
        except Exception as e:
            await self.session.rollback()
            raise APIException(
                error_code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to delete {self.model.__name__}",
            ) from e

        return True

    async def list(
        self,
        organization_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order_desc: bool = False,
        **filters: Any,
    ) -> tuple[list[T], int]:
        """List records with filtering, pagination, and sorting."""
        where_clauses = []

        # Multi-tenancy filter
        if organization_id and hasattr(self.model, "organization_id"):
            where_clauses.append(self.model.organization_id == organization_id)

        # Additional filters
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                where_clauses.append(getattr(self.model, key) == value)

        # Count query
        count_stmt = select(self.model).where(and_(*where_clauses) if where_clauses else True)
        count_result = await self.session.execute(
            select(func.count()).select_from(self.model).where(and_(*where_clauses) if where_clauses else True)
        )
        total = count_result.scalar() or 0

        # List query with sorting
        list_stmt = select(self.model).where(and_(*where_clauses) if where_clauses else True)

        if order_by and hasattr(self.model, order_by):
            order_field = getattr(self.model, order_by)
            list_stmt = list_stmt.order_by(desc(order_field) if order_desc else order_field)

        list_stmt = list_stmt.offset(skip).limit(limit)
        result = await self.session.execute(list_stmt)
        items = result.scalars().all()

        return items, total

    async def exists(
        self,
        id: uuid.UUID,
        organization_id: uuid.UUID | None = None,
    ) -> bool:
        """Check if a record exists."""
        obj = await self.read(id, organization_id)
        return obj is not None
