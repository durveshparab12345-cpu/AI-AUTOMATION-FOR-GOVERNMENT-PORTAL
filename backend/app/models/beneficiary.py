"""
Beneficiary model - represents a healthcare beneficiary/policy holder.

Beneficiaries can have family members (dependents).
Sensitive identifiers are encrypted at rest.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Date, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import Gender, RelationType
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.case import Case


class Beneficiary(BaseModel):
    """
    Beneficiary - the individual receiving healthcare benefits.

    Stores personal identification and demographic information.
    """

    __tablename__ = "beneficiaries"
    __table_args__ = (
        Index("ix_beneficiaries_aadhar", "aadhar"),
        Index("ix_beneficiaries_first_name", "first_name"),
    )

    # Identifiers (encrypted in production)
    aadhar: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )  # 12-digit Aadhar number

    # Demographics
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[Gender | None] = mapped_column(
        String(1),
        nullable=True,
    )  # M, F, O

    # Contact information
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Address
    address_line_1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Family information
    relation_to_primary: Mapped[RelationType] = mapped_column(
        String(20),
        nullable=False,
        default=RelationType.PRIMARY,
    )
    primary_member_id: Mapped[UUID | None] = mapped_column(
        String(36),
        nullable=True,
    )  # ID of primary beneficiary if this is dependent

    # Additional metadata
    eligibility_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    verification_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    verification_details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # JSON

    # Relationships
    cases: Mapped[list[Case]] = relationship(
        "Case",
        back_populates="beneficiary",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        name = f"{self.first_name} {self.last_name}" if self.last_name else self.first_name
        return f"<Beneficiary(id={self.id}, name={name})>"

    @property
    def full_name(self) -> str:
        """Get full name of beneficiary."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    def is_eligible(self) -> bool:
        """Check if beneficiary is eligible for coverage."""
        return self.eligibility_status == "ELIGIBLE"

    def is_verified(self) -> bool:
        """Check if beneficiary has been verified."""
        return self.verification_status == "VERIFIED"
