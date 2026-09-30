"""
AuditLog model for immutable audit trail.

Every data change is logged here for compliance and debugging.
This table is append-only - records are never updated or deleted.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AuditLog(Base):
    """
    Immutable audit trail - all data modifications logged here.

    Does NOT inherit from BaseModel because:
    1. Audit logs are never updated or deleted (immutable)
    2. Audit logs have different tracking requirements
    3. Records their own creation timestamp
    """

    __tablename__ = "audit_logs"

    # Indexes for common queries
    __table_args__ = (
        Index("ix_audit_logs_tenant_id", "tenant_id"),
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_resource_type", "resource_type"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_created_at", "created_at"),
        Index(
            "ix_audit_logs_tenant_resource",
            "tenant_id",
            "resource_type",
            "resource_id",
        ),
    )

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Request context
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    request_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # User who performed the action
    user_id: Mapped[UUID | None] = mapped_column(String(36), nullable=True, index=True)
    user_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Action details
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # CREATE, READ, UPDATE, DELETE, etc.
    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # CASE, USER, WORKFLOW, etc.
    resource_id: Mapped[UUID | None] = mapped_column(
        String(36),
        nullable=True,
    )  # ID of the affected resource

    # Data changes
    old_values: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # JSON of old values
    new_values: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # JSON of new values

    # Result
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="SUCCESS",
    )  # SUCCESS or FAILURE
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Request context
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Timestamp (immutable, append-only table)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default="now()",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"<AuditLog(id={self.id}, action={self.action}, "
            f"resource_type={self.resource_type}, status={self.status})>"
        )

    def is_success(self) -> bool:
        """Check if this audit log records a successful operation."""
        return self.status == "SUCCESS"

    def is_failure(self) -> bool:
        """Check if this audit log records a failed operation."""
        return self.status == "FAILURE"

    organization: Mapped[Organization] = relationship(  # noqa: F821
        "Organization", back_populates="audit_logs"
    )
