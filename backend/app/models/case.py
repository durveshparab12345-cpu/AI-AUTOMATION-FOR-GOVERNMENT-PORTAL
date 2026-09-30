"""
Case model - central business entity representing a healthcare claim.

This is the REAL case model used in production.
Keep app/models/demo_case.py for backward compatibility with demo workflows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Text, Integer, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import CaseStatus, CasePriority
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.beneficiary import Beneficiary
    from app.models.execution import AutomationExecution
    from app.models.automation import Automation
    from app.models.document import Document


class Case(BaseModel):
    """
    Case represents a healthcare claim/reimbursement request.

    Lifecycle:
    INITIATED → ADMISSION_VERIFIED → PREAUTH_SUBMITTED → PREAUTH_APPROVED 
    → TREATMENT_STARTED → TREATMENT_IN_PROGRESS → TREATMENT_COMPLETED 
    → DISCHARGE_INITIATED → DISCHARGE_COMPLETED → CLAIM_SUBMITTED 
    → CLAIM_APPROVED → CLOSED
    """

    __tablename__ = "cases"
    __table_args__ = (
        Index("ix_cases_tenant_status", "tenant_id", "status"),
        Index("ix_cases_case_number", "case_number"),
        Index("ix_cases_beneficiary_id", "beneficiary_id"),
    )

    # Identifiers
    case_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )  # Human-readable case ID

    # State machine
    status: Mapped[CaseStatus] = mapped_column(
        SQLEnum(CaseStatus),
        nullable=False,
        default=CaseStatus.INITIATED,
        index=True,
    )

    # Priority & assignment
    priority: Mapped[CasePriority] = mapped_column(
        SQLEnum(CasePriority),
        nullable=False,
        default=CasePriority.NORMAL,
    )
    assigned_to: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relations to domain entities
    beneficiary_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("beneficiaries.id", ondelete="SET NULL"),
        nullable=True,
    )
    admission_id: Mapped[UUID | None] = mapped_column(String(36), nullable=True)
    preauth_id: Mapped[UUID | None] = mapped_column(String(36), nullable=True)
    treatment_id: Mapped[UUID | None] = mapped_column(String(36), nullable=True)
    discharge_id: Mapped[UUID | None] = mapped_column(String(36), nullable=True)
    claim_id: Mapped[UUID | None] = mapped_column(String(36), nullable=True)

    # Metadata
    case_metadata: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # JSON for extensibility
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    beneficiary: Mapped[Beneficiary | None] = relationship(
        "Beneficiary",
        back_populates="cases",
        foreign_keys=[beneficiary_id],
    )
    executions: Mapped[list[AutomationExecution]] = relationship(
        "AutomationExecution",
        back_populates="case",
        cascade="all, delete-orphan",
    )
    automations: Mapped[list[Automation]] = relationship(
        "Automation",
        back_populates="case",
        cascade="all, delete-orphan",
    )
    documents: Mapped[list[Document]] = relationship(
        "Document",
        back_populates="case",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"<Case(id={self.id}, case_number={self.case_number}, "
            f"status={self.status.value})>"
        )

    def can_transition_to(self, new_status: CaseStatus) -> bool:
        """Check if transition from current status to new_status is valid."""
        from app.core.constants import CASE_STATE_TRANSITIONS

        valid_transitions = CASE_STATE_TRANSITIONS.get(self.status, [])
        return new_status in valid_transitions

    def transition_to(self, new_status: CaseStatus, updated_by: UUID) -> None:
        """
        Transition case to a new status with validation.

        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Cannot transition from {self.status.value} to {new_status.value}"
            )
        self.status = new_status
        self.updated_by = updated_by

    @property
    def is_closed(self) -> bool:
        """Check if case is in a terminal state."""
        return self.status in (CaseStatus.CLOSED, CaseStatus.CANCELLED)

    @property
    def is_preauth_required(self) -> bool:
        """Check if case requires pre-authorization."""
        # TODO: Check against package rules
        return self.status in (
            CaseStatus.INITIATED,
            CaseStatus.ADMISSION_VERIFIED,
            CaseStatus.PREAUTH_SUBMITTED,
        )

    @property
    def is_in_treatment(self) -> bool:
        """Check if case is currently in treatment phase."""
        return self.status in (
            CaseStatus.TREATMENT_STARTED,
            CaseStatus.TREATMENT_IN_PROGRESS,
        )

    @property
    def is_claim_submitted(self) -> bool:
        """Check if claim has been submitted."""
        return self.status in (
            CaseStatus.CLAIM_SUBMITTED,
            CaseStatus.CLAIM_APPROVED,
            CaseStatus.CLAIM_REJECTED,
        )
