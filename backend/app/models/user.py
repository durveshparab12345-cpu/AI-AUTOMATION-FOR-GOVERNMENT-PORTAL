"""
User model — platform users scoped to an organization.

Updated to use BaseModel with audit fields and proper RBAC integration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user_role import UserRole


class User(BaseModel):
    """
    User model - platform user within an organization.

    Every user belongs to exactly one organization (tenant).
    Users have roles that grant permissions within that organization.
    """

    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_is_active", "is_active"),
    )

    # Basic information
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Legacy field (kept for backward compatibility, but not used)
    # New RBAC uses roles instead
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    user_roles: Mapped[list[UserRole]] = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<User(id={self.id}, email={self.email})>"

    @property
    def full_name(self) -> str:
        """Get full name of user."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    def get_active_roles(self) -> list:
        """Get all currently active roles assigned to this user."""
        return [ur.role for ur in self.user_roles if ur.is_active()]

    def get_all_permissions(self) -> set[tuple[str, str]]:
        """
        Get all (resource, action) permissions from active roles.

        Returns:
            Set of (resource, action) tuples
        """
        permissions: set[tuple[str, str]] = set()
        for role in self.get_active_roles():
            for resource, action in role.get_permissions():
                permissions.add((resource, action))
        return permissions

    def has_permission(self, resource: str, action: str) -> bool:
        """
        Check if user has a specific permission.

        Args:
            resource: Resource type (e.g., 'CASE')
            action: Action type (e.g., 'CREATE')

        Returns:
            True if user has this permission via any active role
        """
        return (resource, action) in self.get_all_permissions()

    def has_role(self, role_name: str) -> bool:
        """
        Check if user has a specific role.

        Args:
            role_name: Name of the role (e.g., 'ADMIN', 'OPERATOR')

        Returns:
            True if user has this role and it's active
        """
        for ur in self.user_roles:
            if ur.is_active() and ur.role.name == role_name:
                return True
        return False

    def assign_role(self, role) -> None:  # type: ignore
        """Assign a role to this user."""
        from app.models.user_role import UserRole

        # Check if already assigned
        for ur in self.user_roles:
            if ur.role_id == role.id:
                if not ur.is_active():
                    ur.revoked_at = None  # Re-activate
                return

        # Create new assignment
        ur = UserRole(user_id=self.id, role_id=role.id)
        self.user_roles.append(ur)

    def revoke_role(self, role) -> None:  # type: ignore
        """Revoke a role from this user."""
        for ur in self.user_roles:
            if ur.role_id == role.id and ur.is_active():
                ur.revoke()
