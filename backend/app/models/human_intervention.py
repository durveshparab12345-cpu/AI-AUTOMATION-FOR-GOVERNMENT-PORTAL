"""
HumanIntervention model — tracks pauses for human decision-making in automation.

When automation encounters a situation requiring human judgment, it pauses
and creates a human intervention request.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Text, Enum as SQLEnum, ForeignKey, Index, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.automation import Automation
    from app.models.automation_step import AutomationStep


class HumanIntervention(BaseModel):
    """
    Human intervention request during automation.
    
    Pauses automation and presents a decision or action to a human operator.
    Tracks the intervention, decision, and outcome.
    """

    __tablename__ = "human_interventions"
    __table_args__ = (
        Index("ix_human_interventions_automation_id", "automation_id"),
        Index("ix_human_interventions_status", "status"),
    )

    # References
    automation_id: Mapped[UUID] = mapped_column(
        ForeignKey("automations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    automation_step_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("automation_steps.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Intervention details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING",  # PENDING, APPROVED, REJECTED, ACKNOWLEDGED
    )

    # Decision
    decision: Mapped[str | None] = mapped_column(String(50), nullable=True)
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    decided_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Escalation
    is_escalated: Mapped[bool] = mapped_column(default=False)
    escalated_to: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Expiration
    expires_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    automation: Mapped[Automation] = relationship(
        "Automation",
        back_populates="interventions",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<HumanIntervention(id={self.id}, title={self.title}, status={self.status})>"

    @property
    def is_pending(self) -> bool:
        """Check if intervention is pending decision."""
        return self.status == "PENDING"

    @property
    def is_approved(self) -> bool:
        """Check if intervention was approved."""
        return self.status == "APPROVED"

    @property
    def is_rejected(self) -> bool:
        """Check if intervention was rejected."""
        return self.status == "REJECTED"

    @property
    def is_expired(self) -> bool:
        """Check if intervention has expired."""
        from datetime import datetime, timezone
        if self.expires_at and self.status == "PENDING":
            return datetime.now(timezone.utc) > self.expires_at
        return False
