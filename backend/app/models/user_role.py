"""
UserRole join table for many-to-many relationship between User and Role.

Tracks which roles are assigned to each user within a tenant.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.user import User


class UserRole(Base):
    """
    Join table linking User to Role.

    Does NOT inherit from BaseModel because this is a relationship table,
    not a domain entity.
    """

    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_roles"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id: Mapped[UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Timestamps
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default="now()",
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    # Relationships
    user: Mapped[User] = relationship(
        "User",
        back_populates="user_roles",
        foreign_keys=[user_id],
    )
    role: Mapped[Role] = relationship(
        "Role",
        back_populates="user_roles",
        foreign_keys=[role_id],
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"

    def is_active(self) -> bool:
        """Check if this role assignment is currently active."""
        return self.revoked_at is None

    def revoke(self) -> None:
        """Revoke this role assignment."""
        self.revoked_at = datetime.now(timezone.utc)
