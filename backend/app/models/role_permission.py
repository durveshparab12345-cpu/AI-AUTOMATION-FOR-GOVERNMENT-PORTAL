"""
RolePermission join table for many-to-many relationship.

Links Role to Permission with optional conditions/metadata.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.permission import Permission
    from app.models.role import Role


class RolePermission(Base):
    """
    Join table linking Role to Permission.

    Does NOT inherit from BaseModel because this is a relationship table,
    not a domain entity.
    """

    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permissions"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign keys
    role_id: Mapped[UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Optional conditions (JSON stored as text for flexibility)
    # Example: {"scope": "own_organization", "resource_type": "CASE"}
    conditions: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    role: Mapped[Role] = relationship(
        "Role",
        back_populates="role_permissions",
        foreign_keys=[role_id],
    )
    permission: Mapped[Permission] = relationship(
        "Permission",
        foreign_keys=[permission_id],
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"
