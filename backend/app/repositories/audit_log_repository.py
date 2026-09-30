"""
AuditLogRepository — data access for AuditLog (immutable audit trail).

Handles audit-specific queries like:
  - Append-only inserts (no updates)
  - Finding audit logs by resource
  - Finding audit logs by user
  - Timeline queries
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import and_, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for AuditLog model (immutable)."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, AuditLog)

    async def append(
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
    ) -> AuditLog:
        """
        Append a new audit log entry (immutable).

        Audit logs should never be updated or deleted.
        """
        audit_log = await self.create(
            {
                "organization_id": organization_id,
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "request_id": request_id,
                "old_values": old_values,
                "new_values": new_values,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "status": status,
                "error_message": error_message,
            }
        )
        return audit_log

    async def get_resource_timeline(
        self,
        resource_id: uuid.UUID,
        resource_type: str,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[AuditLog], int]:
        """Get all audit logs for a specific resource (timeline)."""
        from sqlalchemy import count

        # Count
        count_result = await self.session.execute(
            select(count(AuditLog.id)).where(
                and_(
                    AuditLog.resource_id == resource_id,
                    AuditLog.resource_type == resource_type,
                    AuditLog.organization_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List (newest first)
        stmt = (
            select(AuditLog)
            .where(
                and_(
                    AuditLog.resource_id == resource_id,
                    AuditLog.resource_type == resource_type,
                    AuditLog.organization_id == organization_id,
                )
            )
            .order_by(desc(AuditLog.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        logs = result.scalars().all()

        return logs, total

    async def get_user_activity(
        self,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[AuditLog], int]:
        """Get all audit logs for a specific user."""
        from sqlalchemy import count

        # Count
        count_result = await self.session.execute(
            select(count(AuditLog.id)).where(
                and_(
                    AuditLog.user_id == user_id,
                    AuditLog.organization_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List (newest first)
        stmt = (
            select(AuditLog)
            .where(
                and_(
                    AuditLog.user_id == user_id,
                    AuditLog.organization_id == organization_id,
                )
            )
            .order_by(desc(AuditLog.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        logs = result.scalars().all()

        return logs, total

    async def get_by_request_id(
        self,
        request_id: str,
        organization_id: uuid.UUID,
    ) -> list[AuditLog]:
        """Get all audit logs for a specific request."""
        stmt = (
            select(AuditLog)
            .where(
                and_(
                    AuditLog.request_id == request_id,
                    AuditLog.organization_id == organization_id,
                )
            )
            .order_by(AuditLog.created_at)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_failed_operations(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[AuditLog], int]:
        """Get failed operations (status='FAILURE')."""
        from sqlalchemy import count

        # Count
        count_result = await self.session.execute(
            select(count(AuditLog.id)).where(
                and_(
                    AuditLog.organization_id == organization_id,
                    AuditLog.status == "FAILURE",
                )
            )
        )
        total = count_result.scalar() or 0

        # List (newest first)
        stmt = (
            select(AuditLog)
            .where(
                and_(
                    AuditLog.organization_id == organization_id,
                    AuditLog.status == "FAILURE",
                )
            )
            .order_by(desc(AuditLog.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        logs = result.scalars().all()

        return logs, total

    # Override delete and update to prevent modifications
    async def update(self, *args, **kwargs):
        """Audit logs are immutable — cannot be updated."""
        raise RuntimeError("Audit logs cannot be updated (immutable)")

    async def delete(self, *args, **kwargs):
        """Audit logs are immutable — cannot be deleted."""
        raise RuntimeError("Audit logs cannot be deleted (immutable)")
