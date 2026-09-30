"""
API endpoints for exception tracking.

Endpoints:
    POST   /api/v1/exceptions              - Create exception
    GET    /api/v1/exceptions              - List exceptions
    GET    /api/v1/exceptions/{id}         - Get exception
    PUT    /api/v1/exceptions/{id}         - Update exception
    DELETE /api/v1/exceptions/{id}         - Delete exception
    POST   /api/v1/exceptions/search       - Search by error code
    POST   /api/v1/exceptions/{id}/resolve - Mark as resolved
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.core.dependencies import get_current_user
from app.services.exception_service import ExceptionService
from app.models.user import User

router = APIRouter(prefix="/exceptions", tags=["exceptions"])


# ============================================================================
# SCHEMAS
# ============================================================================

class ExceptionCreateRequest(BaseModel):
    """Request schema for creating an exception."""

    automation_id: uuid.UUID = Field(..., description="Associated automation ID")
    error_code: str = Field(..., min_length=1, max_length=50, description="Error code")
    error_type: str = Field(..., min_length=1, max_length=100, description="Error type")
    message: str = Field(..., min_length=1, description="Error message")
    stack_trace: str | None = Field(None, description="Stack trace")
    context_data: str | None = Field(None, description="Context data (JSON)")


class ExceptionUpdateRequest(BaseModel):
    """Request schema for updating an exception."""

    message: str | None = Field(None, min_length=1)
    stack_trace: str | None = Field(None)
    context_data: str | None = Field(None)
    resolution_status: str | None = Field(None, max_length=50)
    resolution_notes: str | None = Field(None)


class ExceptionResolveRequest(BaseModel):
    """Request schema for resolving an exception."""

    resolution_notes: str | None = Field(None, description="Resolution notes")


class ExceptionResponse(BaseModel):
    """Response schema for exception."""

    id: str
    automation_id: str
    error_code: str
    error_type: str
    message: str
    stack_trace: str | None
    context_data: str | None
    resolution_status: str
    resolution_notes: str | None
    resolved_at: str | None
    resolved_by: str | None
    retry_count: int
    max_retries: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ExceptionListResponse(BaseModel):
    """Response schema for exception list."""

    items: list[ExceptionResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "",
    response_model=ExceptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create exception",
)
async def create_exception(
    request: ExceptionCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Record a new exception."""
    try:
        service = ExceptionService(session)
        exception = await service.create(
            tenant_id=current_user.tenant_id,
            automation_id=request.automation_id,
            error_code=request.error_code,
            error_type=request.error_type,
            message=request.message,
            stack_trace=request.stack_trace,
            context_data=request.context_data,
        )

        return {
            "id": str(exception.id),
            "automation_id": str(exception.automation_id),
            "error_code": exception.error_code,
            "error_type": exception.error_type,
            "message": exception.message,
            "stack_trace": exception.stack_trace,
            "context_data": exception.context_data,
            "resolution_status": exception.resolution_status,
            "resolution_notes": exception.resolution_notes,
            "resolved_at": exception.resolved_at.isoformat() if exception.resolved_at else None,
            "resolved_by": exception.resolved_by,
            "retry_count": exception.retry_count,
            "max_retries": exception.max_retries,
            "created_at": exception.created_at.isoformat(),
            "updated_at": exception.updated_at.isoformat(),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=ExceptionListResponse,
    summary="List exceptions",
)
async def list_exceptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    error_code: str | None = Query(None),
    resolution_status: str | None = Query(None),
    automation_id: uuid.UUID | None = Query(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """List exceptions for the organization."""
    try:
        service = ExceptionService(session)
        exceptions, total = await service.list(
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            error_code=error_code,
            resolution_status=resolution_status,
            automation_id=automation_id,
        )

        items = [
            {
                "id": str(e.id),
                "automation_id": str(e.automation_id),
                "error_code": e.error_code,
                "error_type": e.error_type,
                "message": e.message,
                "stack_trace": e.stack_trace,
                "context_data": e.context_data,
                "resolution_status": e.resolution_status,
                "resolution_notes": e.resolution_notes,
                "resolved_at": e.resolved_at.isoformat() if e.resolved_at else None,
                "resolved_by": e.resolved_by,
                "retry_count": e.retry_count,
                "max_retries": e.max_retries,
                "created_at": e.created_at.isoformat(),
                "updated_at": e.updated_at.isoformat(),
            }
            for e in exceptions
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
    "/{exception_id}",
    response_model=ExceptionResponse,
    summary="Get exception",
)
async def get_exception(
    exception_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Get exception details."""
    try:
        service = ExceptionService(session)
        exception = await service.get(
            tenant_id=current_user.tenant_id,
            exception_id=uuid.UUID(exception_id),
        )

        return {
            "id": str(exception.id),
            "automation_id": str(exception.automation_id),
            "error_code": exception.error_code,
            "error_type": exception.error_type,
            "message": exception.message,
            "stack_trace": exception.stack_trace,
            "context_data": exception.context_data,
            "resolution_status": exception.resolution_status,
            "resolution_notes": exception.resolution_notes,
            "resolved_at": exception.resolved_at.isoformat() if exception.resolved_at else None,
            "resolved_by": exception.resolved_by,
            "retry_count": exception.retry_count,
            "max_retries": exception.max_retries,
            "created_at": exception.created_at.isoformat(),
            "updated_at": exception.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exception ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.put(
    "/{exception_id}",
    response_model=ExceptionResponse,
    summary="Update exception",
)
async def update_exception(
    exception_id: str,
    request: ExceptionUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Update exception details."""
    try:
        service = ExceptionService(session)
        exception = await service.update(
            tenant_id=current_user.tenant_id,
            exception_id=uuid.UUID(exception_id),
            updates=request.model_dump(exclude_unset=True),
        )

        return {
            "id": str(exception.id),
            "automation_id": str(exception.automation_id),
            "error_code": exception.error_code,
            "error_type": exception.error_type,
            "message": exception.message,
            "stack_trace": exception.stack_trace,
            "context_data": exception.context_data,
            "resolution_status": exception.resolution_status,
            "resolution_notes": exception.resolution_notes,
            "resolved_at": exception.resolved_at.isoformat() if exception.resolved_at else None,
            "resolved_by": exception.resolved_by,
            "retry_count": exception.retry_count,
            "max_retries": exception.max_retries,
            "created_at": exception.created_at.isoformat(),
            "updated_at": exception.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exception ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/{exception_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete exception",
)
async def delete_exception(
    exception_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
):
    """Delete an exception (soft delete)."""
    try:
        service = ExceptionService(session)
        await service.delete(
            tenant_id=current_user.tenant_id,
            exception_id=uuid.UUID(exception_id),
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exception ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get(
    "/search/by-code",
    response_model=ExceptionListResponse,
    summary="Search exceptions by error code",
)
async def search_by_error_code(
    error_code: str = Query(..., description="Error code to search"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Search exceptions by error code."""
    try:
        service = ExceptionService(session)
        exceptions, total = await service.search_by_error_code(
            tenant_id=current_user.tenant_id,
            error_code=error_code,
            skip=skip,
            limit=limit,
        )

        items = [
            {
                "id": str(e.id),
                "automation_id": str(e.automation_id),
                "error_code": e.error_code,
                "error_type": e.error_type,
                "message": e.message,
                "stack_trace": e.stack_trace,
                "context_data": e.context_data,
                "resolution_status": e.resolution_status,
                "resolution_notes": e.resolution_notes,
                "resolved_at": e.resolved_at.isoformat() if e.resolved_at else None,
                "resolved_by": e.resolved_by,
                "retry_count": e.retry_count,
                "max_retries": e.max_retries,
                "created_at": e.created_at.isoformat(),
                "updated_at": e.updated_at.isoformat(),
            }
            for e in exceptions
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


@router.post(
    "/{exception_id}/resolve",
    response_model=ExceptionResponse,
    summary="Mark exception as resolved",
)
async def resolve_exception(
    exception_id: str,
    request: ExceptionResolveRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Mark an exception as resolved."""
    try:
        service = ExceptionService(session)
        exception = await service.mark_resolved(
            tenant_id=current_user.tenant_id,
            exception_id=uuid.UUID(exception_id),
            resolution_notes=request.resolution_notes,
            resolved_by=current_user.email,
        )

        return {
            "id": str(exception.id),
            "automation_id": str(exception.automation_id),
            "error_code": exception.error_code,
            "error_type": exception.error_type,
            "message": exception.message,
            "stack_trace": exception.stack_trace,
            "context_data": exception.context_data,
            "resolution_status": exception.resolution_status,
            "resolution_notes": exception.resolution_notes,
            "resolved_at": exception.resolved_at.isoformat() if exception.resolved_at else None,
            "resolved_by": exception.resolved_by,
            "retry_count": exception.retry_count,
            "max_retries": exception.max_retries,
            "created_at": exception.created_at.isoformat(),
            "updated_at": exception.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exception ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
