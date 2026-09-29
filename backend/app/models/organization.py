"""
Organization (tenant) model.

Every piece of data in the platform is scoped to an organization.
This provides the multi-tenant isolation boundary.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships (populated in later stages as models are added)
    users: Mapped[list[User]] = relationship("User", back_populates="organization")  # noqa: F821
    demo_cases: Mapped[list[DemoCase]] = relationship(  # noqa: F821
        "DemoCase", back_populates="organization"
    )
    executions: Mapped[list[AutomationExecution]] = relationship(  # noqa: F821
        "AutomationExecution", back_populates="organization"
    )

    def __repr__(self) -> str:
        return f"<Organization id={self.id} slug={self.slug!r}>"
