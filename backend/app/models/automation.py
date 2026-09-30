"""
Automation model — execution instance of a workflow for a specific case.

Tracks the state and progress of workflow automation execution.
Links workflows, cases, and portals in the automation flow.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Enum as SQLEnum, ForeignKey, Index, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import ExecutionStatus
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.workflow import Workflow
    from app.models.case import Case
    from app.models.portal import Portal
    from app.models.automation_step import AutomationStep
    from app.models.query import Query
    from app.models.human_intervention import HumanIntervention
    from app.models.exception import Exception as ExceptionModel


class Automation(BaseModel):
    """
    Automation instance — execution of a workflow for a case.
    
    Represents the execution of an automated workflow against a specific
    case and portal. Tracks overall status, progress, and outcome.
    """

    __tablename__ = "automations"
    __table_args__ = (
        Index("ix_automations_tenant_status", "tenant_id", "status"),
        Index("ix_automations_case_id", "case_id"),
        Index("ix_automations_workflow_id", "workflow_id"),
        Index("ix_automations_started_at", "started_at"),
    )

    # References
    workflow_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflows.id", ondelete="SET NULL"),
        nullable=True,
    )
    case_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("cases.id", ondelete="SET NULL"),
        nullable=True,
    )
    portal_id: Mapped[UUID] = mapped_column(
        ForeignKey("portals.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Status tracking
    status: Mapped[ExecutionStatus] = mapped_column(
        SQLEnum(ExecutionStatus),
        nullable=False,
        default=ExecutionStatus.PENDING,
        index=True,
    )

    # Execution state
    current_step: Mapped[int] = mapped_column(default=0)
    
    # Timestamps
    started_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Human intervention reason
    waiting_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Error tracking
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Results (JSON)
    result_data: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    automation_config: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    workflow: Mapped[Workflow | None] = relationship(
        "Workflow",
        back_populates="automations",
    )
    case: Mapped[Case | None] = relationship(
        "Case",
        back_populates="automations",
    )
    portal: Mapped[Portal] = relationship("Portal")

    steps: Mapped[list[AutomationStep]] = relationship(
        "AutomationStep",
        back_populates="automation",
        cascade="all, delete-orphan",
    )
    queries: Mapped[list[Query]] = relationship(
        "Query",
        back_populates="automation",
        cascade="all, delete-orphan",
    )
    interventions: Mapped[list[HumanIntervention]] = relationship(
        "HumanIntervention",
        back_populates="automation",
        cascade="all, delete-orphan",
    )
    exceptions: Mapped[list[ExceptionModel]] = relationship(
        "Exception",
        back_populates="automation",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Automation(id={self.id}, status={self.status.value}, workflow_id={self.workflow_id})>"

    @property
    def is_running(self) -> bool:
        """Check if automation is currently running."""
        return self.status == ExecutionStatus.RUNNING

    @property
    def is_waiting(self) -> bool:
        """Check if automation is waiting for human intervention."""
        return self.status == ExecutionStatus.WAITING_FOR_HUMAN

    @property
    def is_completed(self) -> bool:
        """Check if automation has completed."""
        return self.status in (ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED)

    @property
    def is_failed(self) -> bool:
        """Check if automation failed."""
        return self.status == ExecutionStatus.FAILED

    @property
    def duration_seconds(self) -> int | None:
        """Get execution duration in seconds."""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return None
