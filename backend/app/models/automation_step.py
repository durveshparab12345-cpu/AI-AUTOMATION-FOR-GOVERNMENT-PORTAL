"""
AutomationStep model — individual step execution within an automation.

Tracks the execution of each node/step in an automation workflow.
Records status, result, and any errors for debugging.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Text, Enum as SQLEnum, ForeignKey, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import StepStatus
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.automation import Automation
    from app.models.workflow_node import WorkflowNode


class AutomationStep(BaseModel):
    """
    Individual step execution within an automation.
    
    Records what happened at each node during the automation execution.
    """

    __tablename__ = "automation_steps"
    __table_args__ = (
        Index("ix_automation_steps_automation_id", "automation_id"),
        Index("ix_automation_steps_status", "status"),
    )

    # References
    automation_id: Mapped[UUID] = mapped_column(
        ForeignKey("automations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workflow_node_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_nodes.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Step identification
    step_number: Mapped[int] = mapped_column(default=0)
    step_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Execution status
    status: Mapped[StepStatus] = mapped_column(
        SQLEnum(StepStatus),
        nullable=False,
        default=StepStatus.PENDING,
        index=True,
    )

    # Timing
    started_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Results & errors (no secrets)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    automation: Mapped[Automation] = relationship(
        "Automation",
        back_populates="steps",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<AutomationStep(automation_id={self.automation_id}, step_number={self.step_number})>"

    @property
    def is_successful(self) -> bool:
        """Check if step completed successfully."""
        return self.status == StepStatus.SUCCESS

    @property
    def is_failed(self) -> bool:
        """Check if step failed."""
        return self.status == StepStatus.FAILED

    @property
    def duration_seconds(self) -> int | None:
        """Get step duration in seconds."""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return None
