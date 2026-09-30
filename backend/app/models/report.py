"""
Report model — generated reports and analytics.

Tracks generated reports for workflows, automations, cases, and business metrics.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Text, Enum as SQLEnum, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Report(BaseModel):
    """
    Generated report for an organization.
    
    Tracks reports on automation performance, case metrics, workflow efficiency,
    and other business intelligence.
    """

    __tablename__ = "reports"
    __table_args__ = (
        Index("ix_reports_report_type", "report_type"),
        Index("ix_reports_generated_at", "generated_at"),
    )

    # Report classification
    report_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="SUMMARY",  # SUMMARY, DETAILED, PERFORMANCE, COMPLIANCE, AUDIT, CUSTOM
    )

    # Report scope
    scope: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="ORGANIZATION",  # ORGANIZATION, WORKFLOW, PORTAL, CASE, AUTOMATION
    )

    # Report configuration
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Filters applied (JSON)
    filters: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Report content (JSON or structured data)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Report file (if exported)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_format: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        default="PDF",  # PDF, EXCEL, CSV, JSON, HTML
    )

    # Timing
    generated_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    generated_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Performance metrics (JSON)
    metrics: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="GENERATED",  # GENERATING, GENERATED, FAILED, EXPORTED
    )

    # Scheduling (for recurring reports)
    is_scheduled: Mapped[bool] = mapped_column(default=False)
    schedule: Mapped[str | None] = mapped_column(String(100), nullable=True)  # CRON expression

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Report(id={self.id}, report_type={self.report_type}, title={self.title})>"

    @property
    def is_generated(self) -> bool:
        """Check if report has been generated."""
        return self.status in ("GENERATED", "EXPORTED")

    @property
    def is_available(self) -> bool:
        """Check if report is available for download."""
        return self.status == "EXPORTED" and self.file_path is not None

    @property
    def can_export(self) -> bool:
        """Check if report can be exported."""
        return self.status == "GENERATED"
