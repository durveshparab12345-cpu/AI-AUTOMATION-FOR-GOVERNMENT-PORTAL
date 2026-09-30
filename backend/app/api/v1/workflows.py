"""
API endpoints for workflow management.

Endpoints:
    POST   /api/v1/workflows             - Create workflow
    GET    /api/v1/workflows             - List workflows
    GET    /api/v1/workflows/{id}        - Get workflow
    PUT    /api/v1/workflows/{id}        - Update workflow
    DELETE /api/v1/workflows/{id}        - Delete workflow
    POST   /api/v1/workflows/{id}/publish - Publish workflow
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.core.dependencies import get_current_user
from app.services.workflow_service import WorkflowService
from app.models.user import User
from app.core.constants import WorkflowStatus

router = APIRouter(prefix="/workflows", tags=["workflows"])


# ============================================================================
# SCHEMAS
# ============================================================================

class WorkflowCreateRequest(BaseModel):
    """Request schema for creating a workflow."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    tags: str | None = Field(None)


class WorkflowUpdateRequest(BaseModel):
    """Request schema for updating a workflow."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    tags: str | None = Field(None)


class WorkflowResponse(BaseModel):
    """Response schema for workflow."""

    id: str
    name: str
    description: str | None
    status: str
    current_version: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class WorkflowListResponse(BaseModel):
    """Response schema for workflow list."""

    items: list[WorkflowResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create workflow",
)
async def create_workflow(
    request: WorkflowCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Create a new workflow in draft status."""
    try:
        service = WorkflowService(session)
        workflow = await service.create_workflow(
            organization_id=current_user.tenant_id,
            name=request.name,
            description=request.description,
            tags=request.tags,
            created_by=current_user.id,
        )

        return {
            "id": str(workflow.id),
            "name": workflow.name,
            "description": workflow.description,
            "status": workflow.status.value if hasattr(workflow.status, "value") else workflow.status,
            "current_version": workflow.current_version,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=WorkflowListResponse,
    summary="List workflows",
)
async def list_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """List workflows for the organization."""
    try:
        service = WorkflowService(session)
        
        status_enum = None
        if status:
            try:
                status_enum = WorkflowStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status}",
                )

        workflows, total = await service.list_workflows(
            organization_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            status=status_enum,
        )

        items = [
            {
                "id": str(w.id),
                "name": w.name,
                "description": w.description,
                "status": w.status.value if hasattr(w.status, "value") else w.status,
                "current_version": w.current_version,
                "created_at": w.created_at.isoformat(),
                "updated_at": w.updated_at.isoformat(),
            }
            for w in workflows
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
    "/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Get workflow",
)
async def get_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Get workflow details."""
    try:
        service = WorkflowService(session)
        workflow = await service.get_workflow(
            workflow_id=uuid.UUID(workflow_id),
            organization_id=current_user.tenant_id,
        )

        return {
            "id": str(workflow.id),
            "name": workflow.name,
            "description": workflow.description,
            "status": workflow.status.value if hasattr(workflow.status, "value") else workflow.status,
            "current_version": workflow.current_version,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid workflow ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.put(
    "/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Update workflow",
)
async def update_workflow(
    workflow_id: str,
    request: WorkflowUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Update workflow details (draft only)."""
    try:
        service = WorkflowService(session)
        workflow = await service.update_workflow(
            workflow_id=uuid.UUID(workflow_id),
            organization_id=current_user.tenant_id,
            updates=request.model_dump(exclude_unset=True),
            updated_by=current_user.id,
        )

        return {
            "id": str(workflow.id),
            "name": workflow.name,
            "description": workflow.description,
            "status": workflow.status.value if hasattr(workflow.status, "value") else workflow.status,
            "current_version": workflow.current_version,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid workflow ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete workflow",
)
async def delete_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
):
    """Delete a workflow (soft delete)."""
    try:
        service = WorkflowService(session)
        await service.delete_workflow(
            workflow_id=uuid.UUID(workflow_id),
            organization_id=current_user.tenant_id,
            deleted_by=current_user.id,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid workflow ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.post(
    "/{workflow_id}/publish",
    response_model=WorkflowResponse,
    summary="Publish workflow",
)
async def publish_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Publish a workflow (make active)."""
    try:
        service = WorkflowService(session)
        workflow = await service.publish_workflow(
            workflow_id=uuid.UUID(workflow_id),
            organization_id=current_user.tenant_id,
            published_by=current_user.id,
        )

        return {
            "id": str(workflow.id),
            "name": workflow.name,
            "description": workflow.description,
            "status": workflow.status.value if hasattr(workflow.status, "value") else workflow.status,
            "current_version": workflow.current_version,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid workflow ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
