"""
FieldMapping model — maps workflow fields to portal fields.

Enables dynamic field translation between the internal system and
external portals. Supports complex mapping logic and transformations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Text, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.workflow import Workflow


class FieldMapping(BaseModel):
    """
    Field mapping between internal fields and portal fields.
    
    Defines how data is transformed when communicating with external portals.
    Supports static mappings and complex transformation logic.
    """

    __tablename__ = "field_mappings"
    __table_args__ = (
        Index("ix_field_mappings_workflow_id", "workflow_id"),
        Index("ix_field_mappings_mapping_type", "mapping_type"),
    )

    # References
    workflow_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Field names
    portal_field: Mapped[str] = mapped_column(String(255), nullable=False)
    system_field: Mapped[str] = mapped_column(String(255), nullable=False)

    # Mapping type
    mapping_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="DIRECT",  # DIRECT, TRANSFORM, COMPUTED, LOOKUP
    )

    # Transformation logic (JSON)
    transformation_logic: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Direction
    direction: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="BIDIRECTIONAL",  # INPUT, OUTPUT, BIDIRECTIONAL
    )

    # Validation rules (JSON)
    validation_rules: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    is_required: Mapped[bool] = mapped_column(default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    workflow: Mapped[Workflow] = relationship("Workflow")

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"<FieldMapping(workflow_id={self.workflow_id}, "
            f"portal_field={self.portal_field}, system_field={self.system_field})>"
        )

    @property
    def is_bidirectional(self) -> bool:
        """Check if mapping is bidirectional."""
        return self.direction == "BIDIRECTIONAL"

    @property
    def is_input(self) -> bool:
        """Check if mapping is for input."""
        return self.direction in ("INPUT", "BIDIRECTIONAL")

    @property
    def is_output(self) -> bool:
        """Check if mapping is for output."""
        return self.direction in ("OUTPUT", "BIDIRECTIONAL")
