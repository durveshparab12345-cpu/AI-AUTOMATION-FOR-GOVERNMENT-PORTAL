"""
CaseService — business logic for case management.

Handles:
  - Case creation and updates
  - State machine validation (CaseStatus transitions)
  - Case queries and filtering
  - Multi-tenancy enforcement
"""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import CaseStatus, CASE_STATE_TRANSITIONS, ErrorCode
from app.exceptions import APIException
from app.models.case import Case
from app.models.user import User
from app.repositories.case_repository import CaseRepository


class CaseService:
    """Service for case management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CaseRepository(session)

    async def create_case(
        self,
        organization_id: uuid.UUID,
        created_by: User,
        case_reference: str,
        beneficiary_id: uuid.UUID,
        hospital_name: str,
        admission_date: date,
        **kwargs,
    ) -> Case:
        """Create a new case."""
        # Check case reference uniqueness per organization
        existing = await self.repo.get_by_reference(case_reference, organization_id)
        if existing:
            raise APIException(
                error_code=ErrorCode.ALREADY_EXISTS,
                message=f"Case reference {case_reference} already exists",
            )

        case = await self.repo.create(
            {
                "organization_id": organization_id,
                "case_reference": case_reference,
                "beneficiary_id": beneficiary_id,
                "hospital_name": hospital_name,
                "admission_date": admission_date,
                "created_by": created_by.id,
                "status": CaseStatus.INITIATED.value,
                **kwargs,
            }
        )
        return case

    async def update_case(
        self,
        case_id: uuid.UUID,
        organization_id: uuid.UUID,
        updated_by: User,
        **kwargs,
    ) -> Case:
        """Update case fields."""
        case = await self.repo.read(case_id, organization_id)
        if not case:
            raise APIException(
                error_code=ErrorCode.NOT_FOUND,
                message="Case not found",
            )

        kwargs["updated_by"] = updated_by.id
        updated_case = await self.repo.update(case_id, kwargs, organization_id)
        return updated_case

    async def transition_case_status(
        self,
        case_id: uuid.UUID,
        organization_id: uuid.UUID,
        new_status: str,
        updated_by: User,
    ) -> Case:
        """
        Transition case to a new status (with state machine validation).

        Validates that the transition is allowed by CASE_STATE_TRANSITIONS.
        """
        case = await self.repo.read(case_id, organization_id)
        if not case:
            raise APIException(
                error_code=ErrorCode.NOT_FOUND,
                message="Case not found",
            )

        # Validate transition
        current_status = CaseStatus(case.status)
        try:
            new_status_enum = CaseStatus(new_status)
        except ValueError:
            raise APIException(
                error_code=ErrorCode.INVALID_INPUT,
                message=f"Invalid case status: {new_status}",
            )

        allowed_transitions = CASE_STATE_TRANSITIONS.get(current_status, [])
        if new_status_enum not in allowed_transitions:
            raise APIException(
                error_code=ErrorCode.INVALID_STATE_TRANSITION,
                message=f"Cannot transition from {case.status} to {new_status}. "
                        f"Allowed: {[s.value for s in allowed_transitions]}",
            )

        # Update status and audit fields
        case = await self.repo.update(
            case_id,
            {
                "status": new_status_enum.value,
                "updated_by": updated_by.id,
            },
            organization_id,
        )
        return case

    async def get_case(
        self,
        case_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Case:
        """Get a case with all relations loaded."""
        case = await self.repo.get_with_relations(case_id, organization_id)
        if not case:
            raise APIException(
                error_code=ErrorCode.NOT_FOUND,
                message="Case not found",
            )
        return case

    async def get_case_by_reference(
        self,
        case_reference: str,
        organization_id: uuid.UUID,
    ) -> Case:
        """Get a case by reference number."""
        case = await self.repo.get_by_reference(case_reference, organization_id)
        if not case:
            raise APIException(
                error_code=ErrorCode.NOT_FOUND,
                message=f"Case {case_reference} not found",
            )
        return case

    async def list_cases(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        beneficiary_id: uuid.UUID | None = None,
    ) -> tuple[list[Case], int]:
        """List cases with filtering."""
        if beneficiary_id:
            return await self.repo.list_by_beneficiary(
                beneficiary_id, organization_id, skip, limit
            )

        if status:
            return await self.repo.list_by_status(status, organization_id, skip, limit)

        return await self.repo.list(organization_id, skip, limit)

    async def delete_case(
        self,
        case_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> bool:
        """Delete a case (soft delete via status or hard delete)."""
        # For now, hard delete. In production, implement soft delete.
        success = await self.repo.delete(case_id, organization_id)
        return success
