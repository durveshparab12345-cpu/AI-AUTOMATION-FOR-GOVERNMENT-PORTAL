"""
Base model class with audit fields for all domain models.

All models inherit from BaseModel to get:
- id: UUID primary key
- tenant_id: Multi-tenant isolation
- created_at, updated_at, deleted_at: Timestamps
- created_by, updated_by, deleted_by: User tracking
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class BaseModel(Base):
    """Abstract base model with audit fields and multi-tenancy support."""

    __abstract__ = True

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Multi-tenancy
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Audit: Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default="now()",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default="now()",
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    # Audit: User tracking (stored as UUID string for performance)
    created_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    deleted_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<{self.__class__.__name__}(id={self.id}, tenant_id={self.tenant_id})>"

    def is_deleted(self) -> bool:
        """Check if this model instance is soft-deleted."""
        return self.deleted_at is not None

    def mark_deleted(self, deleted_by: UUID) -> None:
        """Soft-delete this instance."""
        self.deleted_at = datetime.now(timezone.utc)
        self.deleted_by = deleted_by

    def undelete(self) -> None:
        """Restore a soft-deleted instance."""
        self.deleted_at = None
        self.deleted_by = None
