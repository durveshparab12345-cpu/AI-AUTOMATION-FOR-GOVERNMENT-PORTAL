"""
Exception model — tracks errors and exceptions during automation.

Records what went wrong, diagnostic information, and resolution attempts.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Text, ForeignKey, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.automation import Automation


class Exception(BaseModel):
    """
    Exception or error during automation.
    
    Records technical errors, validation failures, and other issues
    that occur during workflow automation.
    """

    __tablename__ = "exceptions"
    __table_args__ = (
        Index("ix_exceptions_automation_id", "automation_id"),
        Index("ix_exceptions_error_code", "error_code"),
    )

    # References
    automation_id: Mapped[UUID] = mapped_column(
        ForeignKey("automations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Error classification
    error_code: Mapped[str] = mapped_column(String(50), nullable=False)
    error_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="UNKNOWN",  # NETWORK, VALIDATION, AUTH, TIMEOUT, DATA_ERROR, UNKNOWN
    )

    # Error details
    message: Mapped[str] = mapped_column(Text, nullable=False)
    stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Context
    context_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON

    # Resolution
    resolution_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING",  # PENDING, RESOLVED, ESCALATED, IGNORED
    )
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Retry tracking
    retry_count: Mapped[int] = mapped_column(default=0)
    max_retries: Mapped[int] = mapped_column(default=3)

    # Relationships
    automation: Mapped[Automation] = relationship(
        "Automation",
        back_populates="exceptions",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Exception(id={self.id}, error_code={self.error_code}, type={self.error_type})>"

    @property
    def is_resolved(self) -> bool:
        """Check if exception is resolved."""
        return self.resolution_status == "RESOLVED"

    @property
    def is_pending_resolution(self) -> bool:
        """Check if exception is pending resolution."""
        return self.resolution_status == "PENDING"

    @property
    def can_retry(self) -> bool:
        """Check if exception can be retried."""
        return self.retry_count < self.max_retries and self.resolution_status == "PENDING"

    @property
    def is_escalated(self) -> bool:
        """Check if exception is escalated."""
        return self.resolution_status == "ESCALATED"
