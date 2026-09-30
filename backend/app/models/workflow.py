"""
Workflow model — represents a business process automation workflow.

Workflows define the steps and logic for automating portal interactions.
Versioning allows evolution of workflows over time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import WorkflowStatus
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.workflow_version import WorkflowVersion
    from app.models.automation import Automation


class Workflow(BaseModel):
    """
    Workflow — definition of an automated business process.
    
    A workflow contains steps that are executed in sequence or based on
    conditional logic. Workflows are versioned to allow changes while
    preserving older versions for reference.
    """

    __tablename__ = "workflows"
    __table_args__ = (
        Index("ix_workflows_tenant_status", "tenant_id", "status"),
        Index("ix_workflows_name", "name"),
    )

    # Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[WorkflowStatus] = mapped_column(
        SQLEnum(WorkflowStatus),
        nullable=False,
        default=WorkflowStatus.DRAFT,
        index=True,
    )

    # Version tracking
    current_version: Mapped[int] = mapped_column(default=1)

    # Category/tags (JSON)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    workflow_config: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    versions: Mapped[list[WorkflowVersion]] = relationship(
        "WorkflowVersion",
        back_populates="workflow",
        cascade="all, delete-orphan",
    )
    automations: Mapped[list[Automation]] = relationship(
        "Automation",
        back_populates="workflow",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Workflow(id={self.id}, name={self.name}, status={self.status.value})>"

    @property
    def is_active(self) -> bool:
        """Check if workflow is active."""
        return self.status == WorkflowStatus.ACTIVE

    @property
    def is_draft(self) -> bool:
        """Check if workflow is in draft status."""
        return self.status == WorkflowStatus.DRAFT

    @property
    def can_edit(self) -> bool:
        """Check if workflow can be edited."""
        return self.status == WorkflowStatus.DRAFT
