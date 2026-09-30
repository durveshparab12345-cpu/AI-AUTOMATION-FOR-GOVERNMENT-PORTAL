"""
ReportService — business logic for report generation and management.

Handles:
- Report CRUD operations
- Report generation with filtering
- File export tracking
- Scheduled report management
"""

from __future__ import annotations

import uuid
import logging
from typing import Any
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report
from app.repositories.report_repository import ReportRepository
from app.core.constants import ErrorCode
from app.exceptions import APIException

logger = logging.getLogger(__name__)


class ReportService:
    """Service for report generation and management."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session
        self.report_repo = ReportRepository(session)

    async def create(
        self,
        tenant_id: uuid.UUID,
        report_type: str,
        scope: str,
        title: str,
        description: str | None = None,
        filters: str | None = None,
        content: str | None = None,
        file_format: str = "PDF",
        generated_by: str | None = None,
        metrics: str | None = None,
    ) -> Report:
        """
        Create a new report.

        Args:
            tenant_id: Organization ID
            report_type: Type (SUMMARY, DETAILED, PERFORMANCE, etc)
            scope: Scope (ORGANIZATION, WORKFLOW, PORTAL, etc)
            title: Report title
            description: Report description
            filters: Filter criteria (JSON)
            content: Report content (JSON or structured)
            file_format: Output format (PDF, EXCEL, CSV, JSON, HTML)
            generated_by: User generating report
            metrics: Performance metrics (JSON)

        Returns:
            Created report

        Raises:
            APIException: If creation fails
        """
        report = await self.report_repo.create({
            "report_type": report_type,
            "scope": scope,
            "title": title,
            "description": description,
            "filters": filters,
            "content": content,
            "file_format": file_format,
            "status": "GENERATING",
            "generated_by": generated_by,
            "metrics": metrics,
            "is_scheduled": False,
        })

        await self.session.commit()
        logger.info(
            f"Report created: {report.id} ({report_type}) for org {tenant_id}"
        )
        return report

    async def get(
        self,
        tenant_id: uuid.UUID,
        report_id: uuid.UUID,
    ) -> Report:
        """
        Get a report by ID.

        Raises:
            APIException: If not found
        """
        report = await self.report_repo.read(report_id)
        if not report:
            raise APIException(
                error_code=ErrorCode.NOT_FOUND,
                message="Report not found",
            )
        return report

    async def list(
        self,
        tenant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        report_type: str | None = None,
        scope: str | None = None,
        status: str | None = None,
    ) -> tuple[list[Report], int]:
        """
        List reports with optional filtering.

        Args:
            tenant_id: Organization ID
            skip: Pagination offset
            limit: Pagination limit
            report_type: Filter by type
            scope: Filter by scope
            status: Filter by status

        Returns:
            Tuple of (reports, total_count)
        """
        if report_type:
            return await self.report_repo.list_by_type(
                report_type, skip, limit
            )

        if scope:
            return await self.report_repo.list_by_scope(scope, skip, limit)

        if status:
            return await self.report_repo.list_by_status(status, skip, limit)

        return await self.report_repo.list(
            skip=skip,
            limit=limit,
            order_by="generated_at",
            order_desc=True,
        )

    async def update(
        self,
        tenant_id: uuid.UUID,
        report_id: uuid.UUID,
        updates: dict[str, Any],
    ) -> Report:
        """
        Update a report.

        Args:
            tenant_id: Organization ID
            report_id: Report ID
            updates: Fields to update

        Returns:
            Updated report

        Raises:
            APIException: If not found
        """
        report = await self.get(tenant_id, report_id)

        # Allow updating certain fields
        allowed_fields = {
            "title",
            "description",
            "content",
            "metrics",
            "status",
            "file_path",
            "file_format",
        }
        updates = {k: v for k, v in updates.items() if k in allowed_fields}

        if updates:
            report = await self.report_repo.update(report_id, updates)

        await self.session.commit()
        logger.info(f"Report updated: {report_id}")
        return report

    async def generate_report(
        self,
        tenant_id: uuid.UUID,
        report_id: uuid.UUID,
        content: str,
        metrics: str | None = None,
    ) -> Report:
        """
        Mark report as generated with content.

        Args:
            tenant_id: Organization ID
            report_id: Report ID
            content: Generated content
            metrics: Performance metrics

        Returns:
            Updated report
        """
        report = await self.get(tenant_id, report_id)

        updates = {
            "content": content,
            "status": "GENERATED",
            "generated_at": datetime.now(timezone.utc),
        }

        if metrics:
            updates["metrics"] = metrics

        report = await self.report_repo.update(report_id, updates)
        await self.session.commit()

        logger.info(f"Report generated: {report_id}")
        return report

    async def export_report(
        self,
        tenant_id: uuid.UUID,
        report_id: uuid.UUID,
        file_path: str,
    ) -> Report:
        """
        Mark report as exported.

        Args:
            tenant_id: Organization ID
            report_id: Report ID
            file_path: Export file path

        Returns:
            Updated report
        """
        report = await self.get(tenant_id, report_id)

        if report.status != "GENERATED":
            raise APIException(
                error_code=ErrorCode.INVALID_STATE_TRANSITION,
                message="Report must be generated before exporting",
            )

        updates = {
            "status": "EXPORTED",
            "file_path": file_path,
        }

        report = await self.report_repo.update(report_id, updates)
        await self.session.commit()

        logger.info(f"Report exported: {report_id} to {file_path}")
        return report

    async def mark_failed(
        self,
        tenant_id: uuid.UUID,
        report_id: uuid.UUID,
        error_message: str | None = None,
    ) -> Report:
        """
        Mark report as failed.

        Args:
            tenant_id: Organization ID
            report_id: Report ID
            error_message: Failure reason

        Returns:
            Updated report
        """
        report = await self.get(tenant_id, report_id)

        updates = {
            "status": "FAILED",
        }

        report = await self.report_repo.update(report_id, updates)
        await self.session.commit()

        logger.info(f"Report marked as failed: {report_id}")
        return report

    async def delete(
        self,
        tenant_id: uuid.UUID,
        report_id: uuid.UUID,
    ) -> bool:
        """
        Delete a report (soft delete).

        Args:
            tenant_id: Organization ID
            report_id: Report ID

        Returns:
            True if deleted

        Raises:
            APIException: If not found
        """
        report = await self.get(tenant_id, report_id)

        # Mark as deleted
        report.mark_deleted(uuid.UUID(int=0))

        await self.session.commit()
        logger.info(f"Report deleted: {report_id}")
        return True

    async def list_scheduled(
        self,
        tenant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Report], int]:
        """List all scheduled reports."""
        return await self.report_repo.list_scheduled(skip, limit)
