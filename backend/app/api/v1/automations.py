"""
API endpoints for automation execution management.

Endpoints:
    POST   /api/v1/automations              - Create automation
    GET    /api/v1/automations              - List automations
    GET    /api/v1/automations/{id}         - Get automation
    POST   /api/v1/automations/{id}/start   - Start automation
    POST   /api/v1/automations/{id}/pause   - Pause for human intervention
    POST   /api/v1/automations/{id}/resume  - Resume automation
    POST   /api/v1/automations/{id}/complete - Complete automation
    POST   /api/v1/automations/{id}/cancel  - Cancel automation
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.core.dependencies import get_current_user
from app.services.automation_service import AutomationService
from app.models.user import User
from app.core.constants import ExecutionStatus

router = APIRouter(prefix="/automations", tags=["automations"])


# ============================================================================
# SCHEMAS
# ============================================================================

class AutomationCreateRequest(BaseModel):
    """Request schema for creating automation."""

    workflow_id: str = Field(..., description="Workflow to execute")
    portal_id: str = Field(..., description="Portal to interact with")
    case_id: str | None = Field(None, description="Associated case")


class PauseAutomationRequest(BaseModel):
    """Request schema for pausing automation."""

    reason: str = Field(..., min_length=1, max_length=1000, description="Reason for pause")


class AutomationResponse(BaseModel):
    """Response schema for automation."""

    id: str
    workflow_id: str | None
    case_id: str | None
    portal_id: str
    status: str
    current_step: int
    started_at: str | None
    completed_at: str | None
    waiting_reason: str | None
    error_message: str | None
    created_at: str

    class Config:
        from_attributes = True


class AutomationListResponse(BaseModel):
    """Response schema for automation list."""

    items: list[AutomationResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "",
    response_model=AutomationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create automation",
)
async def create_automation(
    request: AutomationCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Create a new automation instance."""
    try:
        service = AutomationService(session)
        automation = await service.create_automation(
            organization_id=current_user.tenant_id,
            workflow_id=uuid.UUID(request.workflow_id),
            portal_id=uuid.UUID(request.portal_id),
            case_id=uuid.UUID(request.case_id) if request.case_id else None,
            created_by=current_user.id,
        )

        return {
            "id": str(automation.id),
            "workflow_id": str(automation.workflow_id) if automation.workflow_id else None,
            "case_id": str(automation.case_id) if automation.case_id else None,
            "portal_id": str(automation.portal_id),
            "status": automation.status.value if hasattr(automation.status, "value") else automation.status,
            "current_step": automation.current_step,
            "started_at": automation.started_at.isoformat() if automation.started_at else None,
            "completed_at": automation.completed_at.isoformat() if automation.completed_at else None,
            "waiting_reason": automation.waiting_reason,
            "error_message": automation.error_message,
            "created_at": automation.created_at.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID: {str(e)}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=AutomationListResponse,
    summary="List automations",
)
async def list_automations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """List automations for the organization."""
    try:
        service = AutomationService(session)
        
        status_enum = None
        if status:
            try:
                status_enum = ExecutionStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status}",
                )

        automations, total = await service.list_automations(
            organization_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            status=status_enum,
        )

        items = [
            {
                "id": str(a.id),
                "workflow_id": str(a.workflow_id) if a.workflow_id else None,
                "case_id": str(a.case_id) if a.case_id else None,
                "portal_id": str(a.portal_id),
                "status": a.status.value if hasattr(a.status, "value") else a.status,
                "current_step": a.current_step,
                "started_at": a.started_at.isoformat() if a.started_at else None,
                "completed_at": a.completed_at.isoformat() if a.completed_at else None,
                "waiting_reason": a.waiting_reason,
                "error_message": a.error_message,
                "created_at": a.created_at.isoformat(),
            }
            for a in automations
        ]

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get(
    "/{automation_id}",
    response_model=AutomationResponse,
    summary="Get automation",
)
async def get_automation(
    automation_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Get automation details."""
    try:
        service = AutomationService(session)
        automation = await service.get_automation(
            automation_id=uuid.UUID(automation_id),
            organization_id=current_user.tenant_id,
        )

        return {
            "id": str(automation.id),
            "workflow_id": str(automation.workflow_id) if automation.workflow_id else None,
            "case_id": str(automation.case_id) if automation.case_id else None,
            "portal_id": str(automation.portal_id),
            "status": automation.status.value if hasattr(automation.status, "value") else automation.status,
            "current_step": automation.current_step,
            "started_at": automation.started_at.isoformat() if automation.started_at else None,
            "completed_at": automation.completed_at.isoformat() if automation.completed_at else None,
            "waiting_reason": automation.waiting_reason,
            "error_message": automation.error_message,
            "created_at": automation.created_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid automation ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.post(
    "/{automation_id}/start",
    response_model=AutomationResponse,
    summary="Start automation",
)
async def start_automation(
    automation_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Start an automation."""
    try:
        service = AutomationService(session)
        automation = await service.start_automation(
            automation_id=uuid.UUID(automation_id),
            organization_id=current_user.tenant_id,
        )

        return {
            "id": str(automation.id),
            "workflow_id": str(automation.workflow_id) if automation.workflow_id else None,
            "case_id": str(automation.case_id) if automation.case_id else None,
            "portal_id": str(automation.portal_id),
            "status": automation.status.value if hasattr(automation.status, "value") else automation.status,
            "current_step": automation.current_step,
            "started_at": automation.started_at.isoformat() if automation.started_at else None,
            "completed_at": automation.completed_at.isoformat() if automation.completed_at else None,
            "waiting_reason": automation.waiting_reason,
            "error_message": automation.error_message,
            "created_at": automation.created_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid automation ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/{automation_id}/pause",
    response_model=AutomationResponse,
    summary="Pause automation",
)
async def pause_automation(
    automation_id: str,
    request: PauseAutomationRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Pause automation for human intervention."""
    try:
        service = AutomationService(session)
        automation = await service.pause_for_human_intervention(
            automation_id=uuid.UUID(automation_id),
            organization_id=current_user.tenant_id,
            reason=request.reason,
        )

        return {
            "id": str(automation.id),
            "workflow_id": str(automation.workflow_id) if automation.workflow_id else None,
            "case_id": str(automation.case_id) if automation.case_id else None,
            "portal_id": str(automation.portal_id),
            "status": automation.status.value if hasattr(automation.status, "value") else automation.status,
            "current_step": automation.current_step,
            "started_at": automation.started_at.isoformat() if automation.started_at else None,
            "completed_at": automation.completed_at.isoformat() if automation.completed_at else None,
            "waiting_reason": automation.waiting_reason,
            "error_message": automation.error_message,
            "created_at": automation.created_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid automation ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/{automation_id}/resume",
    response_model=AutomationResponse,
    summary="Resume automation",
)
async def resume_automation(
    automation_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Resume a paused automation."""
    try:
        service = AutomationService(session)
        automation = await service.resume_automation(
            automation_id=uuid.UUID(automation_id),
            organization_id=current_user.tenant_id,
        )

        return {
            "id": str(automation.id),
            "workflow_id": str(automation.workflow_id) if automation.workflow_id else None,
            "case_id": str(automation.case_id) if automation.case_id else None,
            "portal_id": str(automation.portal_id),
            "status": automation.status.value if hasattr(automation.status, "value") else automation.status,
            "current_step": automation.current_step,
            "started_at": automation.started_at.isoformat() if automation.started_at else None,
            "completed_at": automation.completed_at.isoformat() if automation.completed_at else None,
            "waiting_reason": automation.waiting_reason,
            "error_message": automation.error_message,
            "created_at": automation.created_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid automation ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/{automation_id}/cancel",
    response_model=AutomationResponse,
    summary="Cancel automation",
)
async def cancel_automation(
    automation_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Cancel an automation."""
    try:
        service = AutomationService(session)
        automation = await service.cancel_automation(
            automation_id=uuid.UUID(automation_id),
            organization_id=current_user.tenant_id,
        )

        return {
            "id": str(automation.id),
            "workflow_id": str(automation.workflow_id) if automation.workflow_id else None,
            "case_id": str(automation.case_id) if automation.case_id else None,
            "portal_id": str(automation.portal_id),
            "status": automation.status.value if hasattr(automation.status, "value") else automation.status,
            "current_step": automation.current_step,
            "started_at": automation.started_at.isoformat() if automation.started_at else None,
            "completed_at": automation.completed_at.isoformat() if automation.completed_at else None,
            "waiting_reason": automation.waiting_reason,
            "error_message": automation.error_message,
            "created_at": automation.created_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid automation ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
