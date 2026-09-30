"""
Case schemas for request/response validation.

Covers case creation, updates, queries, and responses.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.core.constants import CaseStatus, CasePriority, AdmissionType


class BeneficiaryBase(BaseModel):
    """Base beneficiary information."""

    pmjay_id: str = Field(..., min_length=1, description="PM-JAY ID")
    first_name: str = Field(..., min_length=1, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    date_of_birth: date = Field(..., description="Date of birth")
    gender: str = Field(..., regex="^[MFO]$", description="Gender (M/F/O)")


class BeneficiaryResponse(BeneficiaryBase):
    """Beneficiary response."""

    id: uuid.UUID
    organization_id: uuid.UUID
    aadhar_number: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaseCreate(BaseModel):
    """Create case request."""

    case_reference: str = Field(..., min_length=1, description="Unique case reference")
    beneficiary_id: uuid.UUID = Field(..., description="Beneficiary ID")
    hospital_name: str = Field(..., min_length=1, description="Hospital name")
    hospital_code: Optional[str] = Field(None, description="Hospital code")
    admission_type: str = Field(
        default=AdmissionType.PLANNED.value,
        regex="^(PLANNED|EMERGENCY)$",
        description="Admission type",
    )
    admission_date: date = Field(..., description="Admission date")
    primary_diagnosis_code: Optional[str] = None
    primary_diagnosis_description: Optional[str] = None
    primary_procedure_code: Optional[str] = None
    primary_procedure_description: Optional[str] = None
    estimated_cost: Optional[float] = Field(None, ge=0, description="Estimated cost")
    priority: str = Field(
        default=CasePriority.NORMAL.value,
        regex="^(LOW|NORMAL|HIGH|CRITICAL)$",
        description="Case priority",
    )
    notes: Optional[str] = None


class CaseUpdate(BaseModel):
    """Update case request (partial)."""

    hospital_name: Optional[str] = None
    hospital_code: Optional[str] = None
    primary_diagnosis_code: Optional[str] = None
    primary_diagnosis_description: Optional[str] = None
    primary_procedure_code: Optional[str] = None
    primary_procedure_description: Optional[str] = None
    estimated_cost: Optional[float] = Field(None, ge=0)
    approved_cost: Optional[float] = Field(None, ge=0)
    priority: Optional[str] = None
    notes: Optional[str] = None
    preauth_reference: Optional[str] = None
    preauth_approved_date: Optional[datetime] = None
    claim_reference: Optional[str] = None
    claim_amount: Optional[float] = Field(None, ge=0)
    claim_approved_amount: Optional[float] = Field(None, ge=0)
    discharge_date: Optional[date] = None
    discharge_type: Optional[str] = None


class CaseStatusUpdate(BaseModel):
    """Request to transition case status."""

    new_status: str = Field(
        ...,
        description="New status for the case",
    )


class CaseResponse(BaseModel):
    """Case response."""

    id: uuid.UUID
    organization_id: uuid.UUID
    case_reference: str
    beneficiary_id: uuid.UUID
    hospital_name: str
    hospital_code: Optional[str]
    admission_type: str
    admission_date: date
    status: str
    priority: str
    primary_diagnosis_code: Optional[str]
    primary_diagnosis_description: Optional[str]
    primary_procedure_code: Optional[str]
    primary_procedure_description: Optional[str]
    estimated_cost: Optional[float]
    approved_cost: Optional[float]
    actual_cost: Optional[float]
    preauth_reference: Optional[str]
    preauth_approved_date: Optional[datetime]
    claim_reference: Optional[str]
    claim_amount: Optional[float]
    claim_approved_amount: Optional[float]
    discharge_date: Optional[date]
    discharge_type: Optional[str]
    notes: Optional[str]
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaseTimelineEntry(BaseModel):
    """Single entry in case timeline."""

    status: str
    timestamp: datetime
    changed_by: Optional[str] = None


class CaseTimeline(BaseModel):
    """Case timeline showing status transitions."""

    case_id: uuid.UUID
    timeline: List[CaseTimelineEntry]
