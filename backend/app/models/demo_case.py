"""
DemoCase model — synthetic demonstration data for PM-JAY prototype.

IMPORTANT: This table contains ONLY synthetic, obviously fake data.
           No real patient information must ever be inserted here.
           The demo_is_synthetic flag enforces this contract in code.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DemoCase(Base):
    __tablename__ = "demo_cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # -------------------------------------------------------------------------
    # Demo case identifier — displayed in the UI for selection
    # -------------------------------------------------------------------------
    case_ref: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # e.g. "DEMO-CASE-001"

    # -------------------------------------------------------------------------
    # Synthetic patient / beneficiary data
    # These fields use obviously fictitious values only.
    # -------------------------------------------------------------------------
    demo_patient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    demo_beneficiary_id: Mapped[str] = mapped_column(String(100), nullable=False)
    demo_dob: Mapped[date] = mapped_column(Date, nullable=False)
    demo_gender: Mapped[str] = mapped_column(String(20), nullable=False)
    demo_hospital_name: Mapped[str] = mapped_column(String(255), nullable=False)
    demo_hospital_code: Mapped[str] = mapped_column(String(50), nullable=False)
    demo_procedure_name: Mapped[str] = mapped_column(String(255), nullable=False)
    demo_procedure_code: Mapped[str] = mapped_column(String(50), nullable=False)
    demo_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    demo_documents: Mapped[str] = mapped_column(
        Text, nullable=False, default="[]"
    )  # JSON array of document names

    # -------------------------------------------------------------------------
    # Safety flag — must always be True for records in this table
    # -------------------------------------------------------------------------
    demo_is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    organization: Mapped[Organization] = relationship(  # noqa: F821
        "Organization", back_populates="demo_cases"
    )

    def __repr__(self) -> str:
        return f"<DemoCase id={self.id} ref={self.case_ref!r}>"
