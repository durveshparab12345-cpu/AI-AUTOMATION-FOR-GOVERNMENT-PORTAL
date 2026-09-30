"""
ExceptionService — business logic for exception tracking and analysis.

Handles:
- Exception CRUD operations
- Error code search and classification
- Resolution tracking
- Retry logic
"""

from __future__ import annotations

import uuid
import logging
from typing import Any
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exception import Exception as ExceptionModel
from app.repositories.exception_repository import ExceptionRepository
from app.core.constants import ErrorCode
from app.exceptions import APIException

logger = logging.getLogger(__name__)


class ExceptionService:
    """Service for exception tracking and analysis."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session
        self.exception_repo = ExceptionRepository(session)

    async def create(
        self,
        tenant_id: uuid.UUID,
        automation_id: uuid.UUID,
        error_code: str,
        error_type: str,
        message: str,
        stack_trace: str | None = None,
        context_data: str | None = None,
    ) -> ExceptionModel:
        """
        Create a new exception record.

        Args:
            tenant_id: Organization ID
            automation_id: Associated automation
            error_code: Error code
            error_type: Error type (NETWORK, VALIDATION, etc)
            message: Error message
            stack_trace: Stack trace (optional)
            context_data: Context JSON (optional)

        Returns:
            Created exception

        Raises:
            APIException: If creation fails
        """
        exception = await self.exception_repo.create({
            "automation_id": automation_id,
            "error_code": error_code,
            "error_type": error_type,
            "message": message,
            "stack_trace": stack_trace,
            "context_data": context_data,
            "resolution_status": "PENDING",
            "retry_count": 0,
        })

        await self.session.commit()
        logger.info(
            f"Exception created: {exception.id} ({error_code}) for automation {automation_id}"
        )
        return exception

    async def get(
        self,
        tenant_id: uuid.UUID,
        exception_id: uuid.UUID,
    ) -> ExceptionModel:
        """
        Get an exception by ID.

        Raises:
            APIException: If not found
        """
        exception = await self.exception_repo.read(exception_id)
        if not exception:
            raise APIException(
                error_code=ErrorCode.NOT_FOUND,
                message="Exception not found",
            )
        return exception

    async def list(
        self,
        tenant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        error_code: str | None = None,
        resolution_status: str | None = None,
        automation_id: uuid.UUID | None = None,
    ) -> tuple[list[ExceptionModel], int]:
        """
        List exceptions with optional filtering.

        Args:
            tenant_id: Organization ID
            skip: Pagination offset
            limit: Pagination limit
            error_code: Filter by error code
            resolution_status: Filter by status
            automation_id: Filter by automation

        Returns:
            Tuple of (exceptions, total_count)
        """
        if error_code:
            return await self.exception_repo.list_by_error_code(
                error_code, skip, limit
            )

        if resolution_status:
            return await self.exception_repo.list_by_status(
                resolution_status, skip, limit
            )

        if automation_id:
            return await self.exception_repo.list_by_automation(
                automation_id, skip, limit
            )

        return await self.exception_repo.list(
            skip=skip,
            limit=limit,
            order_by="created_at",
            order_desc=True,
        )

    async def update(
        self,
        tenant_id: uuid.UUID,
        exception_id: uuid.UUID,
        updates: dict[str, Any],
    ) -> ExceptionModel:
        """
        Update an exception.

        Args:
            tenant_id: Organization ID
            exception_id: Exception ID
            updates: Fields to update

        Returns:
            Updated exception

        Raises:
            APIException: If not found
        """
        exception = await self.get(tenant_id, exception_id)

        # Allow updating certain fields
        allowed_fields = {
            "message",
            "stack_trace",
            "context_data",
            "resolution_status",
            "resolution_notes",
            "resolved_by",
        }
        updates = {k: v for k, v in updates.items() if k in allowed_fields}

        if updates:
            exception = await self.exception_repo.update(exception_id, updates)

        await self.session.commit()
        logger.info(f"Exception updated: {exception_id}")
        return exception

    async def mark_resolved(
        self,
        tenant_id: uuid.UUID,
        exception_id: uuid.UUID,
        resolution_notes: str | None = None,
        resolved_by: str | None = None,
    ) -> ExceptionModel:
        """
        Mark an exception as resolved.

        Args:
            tenant_id: Organization ID
            exception_id: Exception ID
            resolution_notes: Resolution notes
            resolved_by: User resolving

        Returns:
            Updated exception
        """
        exception = await self.get(tenant_id, exception_id)

        updates = {
            "resolution_status": "RESOLVED",
            "resolution_notes": resolution_notes,
            "resolved_by": resolved_by,
            "resolved_at": datetime.now(timezone.utc),
        }

        exception = await self.exception_repo.update(exception_id, updates)
        await self.session.commit()

        logger.info(f"Exception marked resolved: {exception_id}")
        return exception

    async def increment_retry(
        self,
        tenant_id: uuid.UUID,
        exception_id: uuid.UUID,
    ) -> ExceptionModel:
        """
        Increment retry count.

        Args:
            tenant_id: Organization ID
            exception_id: Exception ID

        Returns:
            Updated exception
        """
        exception = await self.get(tenant_id, exception_id)

        updates = {"retry_count": exception.retry_count + 1}

        exception = await self.exception_repo.update(exception_id, updates)
        await self.session.commit()

        logger.info(f"Exception retry incremented: {exception_id} (count: {exception.retry_count})")
        return exception

    async def delete(
        self,
        tenant_id: uuid.UUID,
        exception_id: uuid.UUID,
    ) -> bool:
        """
        Delete an exception (soft delete).

        Args:
            tenant_id: Organization ID
            exception_id: Exception ID

        Returns:
            True if deleted

        Raises:
            APIException: If not found
        """
        exception = await self.get(tenant_id, exception_id)

        # Mark as deleted
        exception.mark_deleted(uuid.UUID(int=0))

        await self.session.commit()
        logger.info(f"Exception deleted: {exception_id}")
        return True

    async def search_by_error_code(
        self,
        tenant_id: uuid.UUID,
        error_code: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ExceptionModel], int]:
        """Search exceptions by error code."""
        return await self.exception_repo.list_by_error_code(
            error_code, skip, limit
        )

    async def list_unresolved(
        self,
        tenant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ExceptionModel], int]:
        """List all unresolved exceptions."""
        return await self.exception_repo.list_unresolved(skip, limit)
