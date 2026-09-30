"""
WorkflowNode model — individual steps within a workflow version.

Nodes represent actions, decisions, or integrations within a workflow.
They reference specific portal operations or system functions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Text, Enum as SQLEnum, ForeignKey, Index, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.workflow_version import WorkflowVersion


class WorkflowNode(BaseModel):
    """
    Individual node/step within a workflow version.
    
    Represents an action, decision, notification, or integration point
    within the workflow DAG.
    """

    __tablename__ = "workflow_nodes"
    __table_args__ = (
        Index("ix_workflow_nodes_workflow_version_id", "workflow_version_id"),
        Index("ix_workflow_nodes_node_type", "node_type"),
    )

    # Identity
    workflow_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Node classification
    node_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="AUTOMATION",  # AUTOMATION, DECISION, NOTIFICATION, HUMAN_INTERVENTION
    )

    # Node naming
    node_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Configuration (JSON)
    config: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Visual positioning (for UI)
    position_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    position_y: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Next node references (JSON for graph structure)
    next_nodes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    workflow_version: Mapped[WorkflowVersion] = relationship(
        "WorkflowVersion",
        back_populates="nodes",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<WorkflowNode(workflow_version_id={self.workflow_version_id}, node_name={self.node_name})>"
