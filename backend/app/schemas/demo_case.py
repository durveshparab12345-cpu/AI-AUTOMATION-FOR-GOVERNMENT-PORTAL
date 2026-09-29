"""DemoCase schemas."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel


class DemoCaseRead(BaseModel):
    id: uuid.UUID
    case_ref: str
    demo_patient_name: str
    demo_beneficiary_id: str
    demo_dob: date
    demo_gender: str
    demo_hospital_name: str
    demo_hospital_code: str
    demo_procedure_name: str
    demo_procedure_code: str
    demo_amount: float
    demo_documents: str  # JSON string
    demo_is_synthetic: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
