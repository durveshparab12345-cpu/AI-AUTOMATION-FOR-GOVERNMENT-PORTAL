"""
WorkflowVersion model — versioned workflow definitions.

Tracks workflow changes over time. Each version can be independently
executed, allowing rollback and history.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Text, Enum as SQLEnum, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import WorkflowStatus
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.workflow import Workflow
    from app.models.workflow_node import WorkflowNode


class WorkflowVersion(BaseModel):
    """
    Versioned workflow definition.
    
    Contains the complete definition (DAG/state machine) for a workflow
    at a particular point in time.
    """

    __tablename__ = "workflow_versions"
    __table_args__ = (
        Index("ix_workflow_versions_workflow_id", "workflow_id"),
        Index("ix_workflow_versions_status", "status"),
    )

    # Identity
    workflow_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Version tracking
    version: Mapped[int] = mapped_column(Integer, nullable=False)

    # Workflow definition (JSON DAG or state machine)
    definition: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[WorkflowStatus] = mapped_column(
        SQLEnum(WorkflowStatus),
        nullable=False,
        default=WorkflowStatus.DRAFT,
        index=True,
    )

    # Creator tracking
    created_by_user: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Change notes
    change_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    workflow: Mapped[Workflow] = relationship(
        "Workflow",
        back_populates="versions",
    )
    nodes: Mapped[list[WorkflowNode]] = relationship(
        "WorkflowNode",
        back_populates="workflow_version",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<WorkflowVersion(workflow_id={self.workflow_id}, version={self.version})>"
