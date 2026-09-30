"""
AuditService — immutable audit trail management.

Handles:
  - Append-only logging of all data changes
  - Querying audit history (timeline, user activity, etc.)
  - No updates/deletes (immutable)
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.audit_log_repository import AuditLogRepository


class AuditService:
    """Service for audit logging (append-only)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AuditLogRepository(session)

    async def log_action(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID | None,
        action: str,
        resource_type: str,
        resource_id: uuid.UUID,
        request_id: str,
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        status: str = "SUCCESS",
        error_message: str | None = None,
    ) -> None:
        """
        Log an action to the audit trail (immutable append).

        Args:
            organization_id: Organization performing the action
            user_id: User who performed the action
            action: Action type (CREATE, UPDATE, DELETE, etc.)
            resource_type: Type of resource affected
            resource_id: ID of the resource
            request_id: Correlation ID for this request
            old_values: Previous values (for UPDATE/DELETE)
            new_values: New values (for CREATE/UPDATE)
            ip_address: Client IP
            user_agent: User-Agent header
            status: SUCCESS or FAILURE
            error_message: Error details if status is FAILURE
        """
        await self.repo.append(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            request_id=request_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            error_message=error_message,
        )
        await self.session.commit()

    async def get_resource_timeline(
        self,
        resource_id: uuid.UUID,
        resource_type: str,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list, int]:
        """Get timeline of all changes to a resource."""
        return await self.repo.get_resource_timeline(
            resource_id, resource_type, organization_id, skip, limit
        )

    async def get_user_activity(
        self,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list, int]:
        """Get all actions performed by a user."""
        return await self.repo.get_user_activity(user_id, organization_id, skip, limit)

    async def get_request_logs(
        self,
        request_id: str,
        organization_id: uuid.UUID,
    ) -> list:
        """Get all audit logs for a specific request."""
        return await self.repo.get_by_request_id(request_id, organization_id)

    async def get_failed_operations(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list, int]:
        """Get failed operations for investigation."""
        return await self.repo.get_failed_operations(organization_id, skip, limit)
