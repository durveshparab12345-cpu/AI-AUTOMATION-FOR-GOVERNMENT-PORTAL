"""
PortalVersion model — versioned portal configurations.

Tracks all configuration changes to portals over time.
Enables rollback and versioning of portal integrations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Text, Enum as SQLEnum, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import PortalStatus, PortalEnvironment
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.portal import Portal


class PortalVersion(BaseModel):
    """
    Version of a portal configuration.
    
    Each time a portal's configuration changes, a new version is created.
    This allows for easy rollback and history tracking.
    """

    __tablename__ = "portal_versions"
    __table_args__ = (
        Index("ix_portal_versions_portal_id", "portal_id"),
        Index("ix_portal_versions_status", "status"),
    )

    # Identity
    portal_id: Mapped[UUID] = mapped_column(
        ForeignKey("portals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Version tracking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Configuration (JSON)
    config: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Environment this version is for
    environment: Mapped[PortalEnvironment] = mapped_column(
        SQLEnum(PortalEnvironment),
        nullable=False,
        default=PortalEnvironment.DEVELOPMENT,
    )

    # Status
    status: Mapped[PortalStatus] = mapped_column(
        SQLEnum(PortalStatus),
        nullable=False,
        default=PortalStatus.DRAFT,
        index=True,
    )

    # Release notes
    release_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    portal: Mapped[Portal] = relationship(
        "Portal",
        back_populates="versions",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<PortalVersion(portal_id={self.portal_id}, version={self.version})>"
