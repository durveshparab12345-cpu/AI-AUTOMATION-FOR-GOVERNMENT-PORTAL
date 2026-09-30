"""
Query model — tracks queries raised during automation or case processing.

Queries represent questions or clarifications needed from the hospital,
insurance company, or beneficiary during the case workflow.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Text, Enum as SQLEnum, ForeignKey, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import QueryStatus
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.automation import Automation


class Query(BaseModel):
    """
    Query raised during case processing or automation.
    
    Tracks questions, clarifications, and responses needed to progress
    a case through the workflow.
    """

    __tablename__ = "queries"
    __table_args__ = (
        Index("ix_queries_case_id", "case_id"),
        Index("ix_queries_automation_id", "automation_id"),
        Index("ix_queries_status", "status"),
    )

    # References
    case_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=True,
    )
    automation_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("automations.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Query details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Status tracking
    status: Mapped[QueryStatus] = mapped_column(
        SQLEnum(QueryStatus),
        nullable=False,
        default=QueryStatus.OPEN,
        index=True,
    )

    # Response tracking
    response: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    response_from: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Escalation
    is_escalated: Mapped[bool] = mapped_column(default=False)
    escalation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Due date
    due_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    case: Mapped[Case | None] = relationship("Case")
    automation: Mapped[Automation | None] = relationship("Automation", back_populates="queries")

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Query(id={self.id}, title={self.title}, status={self.status.value})>"

    @property
    def is_open(self) -> bool:
        """Check if query is open."""
        return self.status == QueryStatus.OPEN

    @property
    def is_resolved(self) -> bool:
        """Check if query is resolved."""
        return self.status == QueryStatus.RESOLVED

    @property
    def is_overdue(self) -> bool:
        """Check if query is overdue."""
        from datetime import datetime, timezone
        if self.due_date and self.status != QueryStatus.RESOLVED:
            return datetime.now(timezone.utc) > self.due_date
        return False
