"""
Portal model — represents a configured external portal integration.

A portal is a third-party system (PMJAY, TPA, Insurance, Hospital, etc.)
that we need to automate. Each portal has connection details, authentication
settings, and versioned configurations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import PortalStatus, PortalType
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.portal_version import PortalVersion


class Portal(BaseModel):
    """
    Portal configuration and integration details.
    
    Each portal represents an external system we integrate with.
    Versions track configuration changes over time.
    """

    __tablename__ = "portals"
    __table_args__ = (
        Index("ix_portals_tenant_status", "tenant_id", "status"),
        Index("ix_portals_name", "name"),
    )

    # Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Portal type & classification
    type: Mapped[PortalType] = mapped_column(
        SQLEnum(PortalType),
        nullable=False,
        default=PortalType.CUSTOM,
    )

    # Network & connectivity
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Authentication method
    auth_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="BASIC",  # BASIC, OAUTH2, SAML, API_KEY, FORM
    )

    # Status
    status: Mapped[PortalStatus] = mapped_column(
        SQLEnum(PortalStatus),
        nullable=False,
        default=PortalStatus.DRAFT,
        index=True,
    )

    # Metadata (JSON)
    portal_config: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    versions: Mapped[list[PortalVersion]] = relationship(
        "PortalVersion",
        back_populates="portal",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Portal(id={self.id}, name={self.name}, type={self.type.value})>"

    @property
    def is_active(self) -> bool:
        """Check if portal is active."""
        return self.status == PortalStatus.ACTIVE

    @property
    def is_configured(self) -> bool:
        """Check if portal has been configured."""
        return self.status in (PortalStatus.CONFIGURED, PortalStatus.ACTIVE)
