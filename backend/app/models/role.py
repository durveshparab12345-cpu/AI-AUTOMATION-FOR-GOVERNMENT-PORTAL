"""
Role model for Role-Based Access Control (RBAC).

Roles group permissions for easier management.
Each organization can have custom roles.
System roles are shared across all organizations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.permission import Permission
    from app.models.role_permission import RolePermission
    from app.models.user_role import UserRole


class Role(BaseModel):
    """Role model for grouping permissions."""

    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_roles_tenant_name"),
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # System roles are predefined and cannot be deleted
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    role_permissions: Mapped[list[RolePermission]] = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    user_roles: Mapped[list[UserRole]] = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Role(id={self.id}, name={self.name}, is_system={self.is_system})>"

    def has_permission(self, resource: str, action: str) -> bool:
        """
        Check if this role has a specific permission.

        Args:
            resource: Resource type (e.g., 'CASE')
            action: Action type (e.g., 'CREATE')

        Returns:
            True if role has this permission
        """
        for rp in self.role_permissions:
            if rp.permission.resource == resource and rp.permission.action == action:
                return True
        return False

    def add_permission(self, permission: Permission) -> None:
        """Add a permission to this role."""
        from app.models.role_permission import RolePermission

        if not self.has_permission(permission.resource, permission.action):
            rp = RolePermission(role_id=self.id, permission_id=permission.id)
            self.role_permissions.append(rp)

    def remove_permission(self, permission: Permission) -> None:
        """Remove a permission from this role."""
        self.role_permissions = [
            rp for rp in self.role_permissions if rp.permission_id != permission.id
        ]

    def get_permissions(self) -> list[tuple[str, str]]:
        """Get all (resource, action) tuples for this role."""
        return [(rp.permission.resource, rp.permission.action) for rp in self.role_permissions]
