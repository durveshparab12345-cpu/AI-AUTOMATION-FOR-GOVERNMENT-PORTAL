"""Execution schemas for request/response."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.execution import ExecutionStatus, StepStatus


class ExecutionStepRead(BaseModel):
    id: uuid.UUID
    step_number: int
    step_name: str
    status: StepStatus
    message: str | None
    started_at: datetime | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class ExecutionRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    demo_case_id: uuid.UUID | None
    workflow_name: str
    initiated_by: str
    status: ExecutionStatus
    current_step: int
    waiting_reason: str | None
    error_message: str | None
    portal_result: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    steps: list[ExecutionStepRead] = []

    model_config = {"from_attributes": True}


class ExecutionCreate(BaseModel):
    demo_case_id: uuid.UUID
    workflow_name: str = "PM-JAY Beneficiary / Case Processing Demo"


class ContinueRequest(BaseModel):
    operator_note: str | None = None


class ValidationResult(BaseModel):
    passed: bool
    checks: list[dict]  # [{name, passed, message}]
