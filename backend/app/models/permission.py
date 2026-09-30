"""
Permission model for fine-grained access control.

Permissions are global (not tenant-specific) and represent
the combination of a resource and an action.

Example:
- CASE + CREATE = can create cases
- WORKFLOW + EXECUTE = can execute workflows
- DOCUMENT + DELETE = can delete documents
"""

from __future__ import annotations

from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Permission(Base):
    """
    Permission model - global permissions shared across all tenants.

    Does NOT inherit from BaseModel because permissions are system-wide,
    not tenant-scoped.
    """

    __tablename__ = "permissions"
    __table_args__ = (
        UniqueConstraint("resource", "action", name="uq_permissions_resource_action"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Resource type (e.g., 'CASE', 'WORKFLOW', 'DOCUMENT')
    resource: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Action type (e.g., 'CREATE', 'READ', 'UPDATE', 'DELETE', 'EXECUTE')
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Human-readable description
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Permission({self.resource}:{self.action})>"

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.resource}:{self.action}"

    def __eq__(self, other: object) -> bool:
        """Check equality by resource and action."""
        if not isinstance(other, Permission):
            return NotImplemented
        return self.resource == other.resource and self.action == other.action

    def __hash__(self) -> int:
        """Make permission hashable."""
        return hash((self.resource, self.action))
