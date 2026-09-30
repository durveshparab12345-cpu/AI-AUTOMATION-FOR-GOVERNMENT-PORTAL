"""
AutomationExecution and AutomationExecutionStep models.

These track every workflow run — what ran, when, what each step did,
and what the final outcome was. These are the audit trail for the prototype.

IMPORTANT: Do NOT store portal passwords, OTP values, session tokens,
           or any authentication secrets in these tables.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ExecutionStatus(str, enum.Enum):
    """
    Explicit finite state machine for workflow executions.
    Using an enum prevents arbitrary string state values scattered in code.
    """

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_FOR_HUMAN = "WAITING_FOR_HUMAN"
    VALIDATING = "VALIDATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class StepStatus(str, enum.Enum):
    """Status for individual execution steps."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_FOR_HUMAN = "WAITING_FOR_HUMAN"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class AutomationExecution(Base):
    __tablename__ = "automation_executions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    demo_case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("demo_cases.id", ondelete="SET NULL"),
        nullable=True,
    )

    workflow_name: Mapped[str] = mapped_column(String(255), nullable=False)
    initiated_by: Mapped[str] = mapped_column(String(255), nullable=False)  # user email

    status: Mapped[ExecutionStatus] = mapped_column(
        Enum(ExecutionStatus, name="execution_status_enum", native_enum=False),
        nullable=False,
        default=ExecutionStatus.PENDING,
        index=True,
    )
    current_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Human-in-the-loop — reason why we are waiting for the operator
    waiting_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Error information (no credentials/tokens stored here)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Portal result — only real values obtained from the portal session
    # NEVER fabricate values here
    portal_result: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string

    # Screenshot path (relative, not publicly accessible)
    last_screenshot_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    organization: Mapped[Organization] = relationship(  # noqa: F821
        "Organization", back_populates="executions"
    )
    case: Mapped[Case] = relationship("Case", back_populates="executions")  # noqa: F821
    demo_case: Mapped[DemoCase] = relationship("DemoCase")  # noqa: F821
    steps: Mapped[list[AutomationExecutionStep]] = relationship(
        "AutomationExecutionStep",
        back_populates="execution",
        order_by="AutomationExecutionStep.step_number",
    )

    def __repr__(self) -> str:
        return f"<AutomationExecution id={self.id} status={self.status}>"


class AutomationExecutionStep(Base):
    __tablename__ = "automation_execution_steps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("automation_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    step_name: Mapped[str] = mapped_column(String(255), nullable=False)

    status: Mapped[StepStatus] = mapped_column(
        Enum(StepStatus, name="step_status_enum", native_enum=False),
        nullable=False,
        default=StepStatus.PENDING,
    )

    # Operator-visible message — no secrets
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata JSON (action taken, element found, etc. — no credentials)
    step_metadata: Mapped[str | None] = mapped_column(Text, nullable=True, name="step_metadata")

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    execution: Mapped[AutomationExecution] = relationship(
        "AutomationExecution", back_populates="steps"
    )

    def __repr__(self) -> str:
        return f"<ExecutionStep #{self.step_number} {self.step_name!r} {self.status}>"
