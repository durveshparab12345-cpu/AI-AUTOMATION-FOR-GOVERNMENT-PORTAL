"""
API endpoints for human intervention management.

Endpoints:
    POST   /api/v1/human_interventions              - Create intervention
    GET    /api/v1/human_interventions              - List interventions
    GET    /api/v1/human_interventions/{id}         - Get intervention
    PUT    /api/v1/human_interventions/{id}         - Update intervention
    DELETE /api/v1/human_interventions/{id}         - Delete intervention
    POST   /api/v1/human_interventions/{id}/approve - Approve intervention
    POST   /api/v1/human_interventions/{id}/reject  - Reject intervention
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.core.dependencies import get_current_user
from app.services.human_intervention_service import HumanInterventionService
from app.models.user import User

router = APIRouter(prefix="/human_interventions", tags=["human_interventions"])


# ============================================================================
# SCHEMAS
# ============================================================================

class HumanInterventionCreateRequest(BaseModel):
    """Request schema for creating an intervention."""

    automation_id: uuid.UUID = Field(..., description="Associated automation ID")
    title: str = Field(..., min_length=1, max_length=255, description="Intervention title")
    description: str = Field(..., min_length=1, description="Detailed description")
    reason: str = Field(..., min_length=1, description="Reason for intervention")
    automation_step_id: uuid.UUID | None = Field(None, description="Associated automation step")
    is_escalated: bool = Field(default=False, description="Whether escalated")
    escalated_to: str | None = Field(None, max_length=255, description="Escalation target")


class HumanInterventionUpdateRequest(BaseModel):
    """Request schema for updating an intervention."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1)
    reason: str | None = Field(None, min_length=1)
    is_escalated: bool | None = Field(None)
    escalated_to: str | None = Field(None, max_length=255)


class HumanInterventionApproveRequest(BaseModel):
    """Request schema for approving an intervention."""

    decision: str | None = Field(None, max_length=100, description="Decision value")
    decision_reason: str | None = Field(None, description="Reason for decision")


class HumanInterventionRejectRequest(BaseModel):
    """Request schema for rejecting an intervention."""

    decision_reason: str | None = Field(None, description="Reason for rejection")


class HumanInterventionResponse(BaseModel):
    """Response schema for intervention."""

    id: str
    automation_id: str
    automation_step_id: str | None
    title: str
    description: str
    reason: str
    status: str
    decision: str | None
    decision_reason: str | None
    decided_by: str | None
    decided_at: str | None
    is_escalated: bool
    escalated_to: str | None
    expires_at: str | None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class HumanInterventionListResponse(BaseModel):
    """Response schema for intervention list."""

    items: list[HumanInterventionResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "",
    response_model=HumanInterventionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create intervention",
)
async def create_intervention(
    request: HumanInterventionCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Create a new human intervention request."""
    try:
        service = HumanInterventionService(session)
        intervention = await service.create(
            tenant_id=current_user.tenant_id,
            automation_id=request.automation_id,
            title=request.title,
            description=request.description,
            reason=request.reason,
            automation_step_id=request.automation_step_id,
            is_escalated=request.is_escalated,
            escalated_to=request.escalated_to,
        )

        return {
            "id": str(intervention.id),
            "automation_id": str(intervention.automation_id),
            "automation_step_id": str(intervention.automation_step_id) if intervention.automation_step_id else None,
            "title": intervention.title,
            "description": intervention.description,
            "reason": intervention.reason,
            "status": intervention.status,
            "decision": intervention.decision,
            "decision_reason": intervention.decision_reason,
            "decided_by": intervention.decided_by,
            "decided_at": intervention.decided_at.isoformat() if intervention.decided_at else None,
            "is_escalated": intervention.is_escalated,
            "escalated_to": intervention.escalated_to,
            "expires_at": intervention.expires_at.isoformat() if intervention.expires_at else None,
            "created_at": intervention.created_at.isoformat(),
            "updated_at": intervention.updated_at.isoformat(),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=HumanInterventionListResponse,
    summary="List interventions",
)
async def list_interventions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    automation_id: uuid.UUID | None = Query(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """List human interventions for the organization."""
    try:
        service = HumanInterventionService(session)
        interventions, total = await service.list(
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            status=status,
            automation_id=automation_id,
        )

        items = [
            {
                "id": str(i.id),
                "automation_id": str(i.automation_id),
                "automation_step_id": str(i.automation_step_id) if i.automation_step_id else None,
                "title": i.title,
                "description": i.description,
                "reason": i.reason,
                "status": i.status,
                "decision": i.decision,
                "decision_reason": i.decision_reason,
                "decided_by": i.decided_by,
                "decided_at": i.decided_at.isoformat() if i.decided_at else None,
                "is_escalated": i.is_escalated,
                "escalated_to": i.escalated_to,
                "expires_at": i.expires_at.isoformat() if i.expires_at else None,
                "created_at": i.created_at.isoformat(),
                "updated_at": i.updated_at.isoformat(),
            }
            for i in interventions
        ]

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get(
    "/{intervention_id}",
    response_model=HumanInterventionResponse,
    summary="Get intervention",
)
async def get_intervention(
    intervention_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Get intervention details."""
    try:
        service = HumanInterventionService(session)
        intervention = await service.get(
            tenant_id=current_user.tenant_id,
            intervention_id=uuid.UUID(intervention_id),
        )

        return {
            "id": str(intervention.id),
            "automation_id": str(intervention.automation_id),
            "automation_step_id": str(intervention.automation_step_id) if intervention.automation_step_id else None,
            "title": intervention.title,
            "description": intervention.description,
            "reason": intervention.reason,
            "status": intervention.status,
            "decision": intervention.decision,
            "decision_reason": intervention.decision_reason,
            "decided_by": intervention.decided_by,
            "decided_at": intervention.decided_at.isoformat() if intervention.decided_at else None,
            "is_escalated": intervention.is_escalated,
            "escalated_to": intervention.escalated_to,
            "expires_at": intervention.expires_at.isoformat() if intervention.expires_at else None,
            "created_at": intervention.created_at.isoformat(),
            "updated_at": intervention.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid intervention ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.put(
    "/{intervention_id}",
    response_model=HumanInterventionResponse,
    summary="Update intervention",
)
async def update_intervention(
    intervention_id: str,
    request: HumanInterventionUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Update intervention details."""
    try:
        service = HumanInterventionService(session)
        intervention = await service.update(
            tenant_id=current_user.tenant_id,
            intervention_id=uuid.UUID(intervention_id),
            updates=request.model_dump(exclude_unset=True),
        )

        return {
            "id": str(intervention.id),
            "automation_id": str(intervention.automation_id),
            "automation_step_id": str(intervention.automation_step_id) if intervention.automation_step_id else None,
            "title": intervention.title,
            "description": intervention.description,
            "reason": intervention.reason,
            "status": intervention.status,
            "decision": intervention.decision,
            "decision_reason": intervention.decision_reason,
            "decided_by": intervention.decided_by,
            "decided_at": intervention.decided_at.isoformat() if intervention.decided_at else None,
            "is_escalated": intervention.is_escalated,
            "escalated_to": intervention.escalated_to,
            "expires_at": intervention.expires_at.isoformat() if intervention.expires_at else None,
            "created_at": intervention.created_at.isoformat(),
            "updated_at": intervention.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid intervention ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/{intervention_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete intervention",
)
async def delete_intervention(
    intervention_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
):
    """Delete an intervention (soft delete)."""
    try:
        service = HumanInterventionService(session)
        await service.delete(
            tenant_id=current_user.tenant_id,
            intervention_id=uuid.UUID(intervention_id),
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid intervention ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.post(
    "/{intervention_id}/approve",
    response_model=HumanInterventionResponse,
    summary="Approve intervention",
)
async def approve_intervention(
    intervention_id: str,
    request: HumanInterventionApproveRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Approve a human intervention."""
    try:
        service = HumanInterventionService(session)
        intervention = await service.update_status(
            tenant_id=current_user.tenant_id,
            intervention_id=uuid.UUID(intervention_id),
            status="APPROVED",
            decision=request.decision,
            decision_reason=request.decision_reason,
            decided_by=current_user.email,
        )

        return {
            "id": str(intervention.id),
            "automation_id": str(intervention.automation_id),
            "automation_step_id": str(intervention.automation_step_id) if intervention.automation_step_id else None,
            "title": intervention.title,
            "description": intervention.description,
            "reason": intervention.reason,
            "status": intervention.status,
            "decision": intervention.decision,
            "decision_reason": intervention.decision_reason,
            "decided_by": intervention.decided_by,
            "decided_at": intervention.decided_at.isoformat() if intervention.decided_at else None,
            "is_escalated": intervention.is_escalated,
            "escalated_to": intervention.escalated_to,
            "expires_at": intervention.expires_at.isoformat() if intervention.expires_at else None,
            "created_at": intervention.created_at.isoformat(),
            "updated_at": intervention.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid intervention ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/{intervention_id}/reject",
    response_model=HumanInterventionResponse,
    summary="Reject intervention",
)
async def reject_intervention(
    intervention_id: str,
    request: HumanInterventionRejectRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Reject a human intervention."""
    try:
        service = HumanInterventionService(session)
        intervention = await service.update_status(
            tenant_id=current_user.tenant_id,
            intervention_id=uuid.UUID(intervention_id),
            status="REJECTED",
            decision_reason=request.decision_reason,
            decided_by=current_user.email,
        )

        return {
            "id": str(intervention.id),
            "automation_id": str(intervention.automation_id),
            "automation_step_id": str(intervention.automation_step_id) if intervention.automation_step_id else None,
            "title": intervention.title,
            "description": intervention.description,
            "reason": intervention.reason,
            "status": intervention.status,
            "decision": intervention.decision,
            "decision_reason": intervention.decision_reason,
            "decided_by": intervention.decided_by,
            "decided_at": intervention.decided_at.isoformat() if intervention.decided_at else None,
            "is_escalated": intervention.is_escalated,
            "escalated_to": intervention.escalated_to,
            "expires_at": intervention.expires_at.isoformat() if intervention.expires_at else None,
            "created_at": intervention.created_at.isoformat(),
            "updated_at": intervention.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid intervention ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
