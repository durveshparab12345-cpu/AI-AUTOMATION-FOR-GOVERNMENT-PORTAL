"""
API endpoints for report management.

Endpoints:
    POST   /api/v1/reports                    - Create report
    GET    /api/v1/reports                    - List reports
    GET    /api/v1/reports/{id}               - Get report
    PUT    /api/v1/reports/{id}               - Update report
    DELETE /api/v1/reports/{id}               - Delete report
    POST   /api/v1/reports/{id}/generate      - Generate report
    POST   /api/v1/reports/{id}/export        - Export report
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.core.dependencies import get_current_user
from app.services.report_service import ReportService
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["reports"])


# ============================================================================
# SCHEMAS
# ============================================================================

class ReportCreateRequest(BaseModel):
    """Request schema for creating a report."""

    report_type: str = Field(..., min_length=1, max_length=100, description="Report type")
    scope: str = Field(..., min_length=1, max_length=50, description="Report scope")
    title: str = Field(..., min_length=1, max_length=255, description="Report title")
    description: str | None = Field(None, description="Report description")
    filters: str | None = Field(None, description="Filter criteria (JSON)")
    metrics: str | None = Field(None, description="Metrics to include (JSON)")


class ReportUpdateRequest(BaseModel):
    """Request schema for updating a report."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None)
    status: str | None = Field(None, max_length=50)


class ReportGenerateRequest(BaseModel):
    """Request schema for generating a report."""

    content: str = Field(..., description="Generated report content")
    metrics: str | None = Field(None, description="Performance metrics (JSON)")


class ReportExportRequest(BaseModel):
    """Request schema for exporting a report."""

    file_path: str = Field(..., min_length=1, max_length=500, description="Export file path")


class ReportResponse(BaseModel):
    """Response schema for report."""

    id: str
    report_type: str
    scope: str
    title: str
    description: str | None
    status: str
    content: str | None
    file_path: str | None
    file_format: str | None
    generated_at: str | None
    generated_by: str | None
    metrics: str | None
    is_scheduled: bool
    schedule: str | None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    """Response schema for report list."""

    items: list[ReportResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create report",
)
async def create_report(
    request: ReportCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Create a new report."""
    try:
        service = ReportService(session)
        report = await service.create(
            tenant_id=current_user.tenant_id,
            report_type=request.report_type,
            scope=request.scope,
            title=request.title,
            description=request.description,
            filters=request.filters,
            generated_by=current_user.email,
            metrics=request.metrics,
        )

        return {
            "id": str(report.id),
            "report_type": report.report_type,
            "scope": report.scope,
            "title": report.title,
            "description": report.description,
            "status": report.status,
            "content": report.content,
            "file_path": report.file_path,
            "file_format": report.file_format,
            "generated_at": report.generated_at.isoformat() if report.generated_at else None,
            "generated_by": report.generated_by,
            "metrics": report.metrics,
            "is_scheduled": report.is_scheduled,
            "schedule": report.schedule,
            "created_at": report.created_at.isoformat(),
            "updated_at": report.updated_at.isoformat(),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=ReportListResponse,
    summary="List reports",
)
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    report_type: str | None = Query(None),
    scope: str | None = Query(None),
    status: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """List reports for the organization."""
    try:
        service = ReportService(session)
        reports, total = await service.list(
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            report_type=report_type,
            scope=scope,
            status=status,
        )

        items = [
            {
                "id": str(r.id),
                "report_type": r.report_type,
                "scope": r.scope,
                "title": r.title,
                "description": r.description,
                "status": r.status,
                "content": r.content,
                "file_path": r.file_path,
                "file_format": r.file_format,
                "generated_at": r.generated_at.isoformat() if r.generated_at else None,
                "generated_by": r.generated_by,
                "metrics": r.metrics,
                "is_scheduled": r.is_scheduled,
                "schedule": r.schedule,
                "created_at": r.created_at.isoformat(),
                "updated_at": r.updated_at.isoformat(),
            }
            for r in reports
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
    "/{report_id}",
    response_model=ReportResponse,
    summary="Get report",
)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Get report details."""
    try:
        service = ReportService(session)
        report = await service.get(
            tenant_id=current_user.tenant_id,
            report_id=uuid.UUID(report_id),
        )

        return {
            "id": str(report.id),
            "report_type": report.report_type,
            "scope": report.scope,
            "title": report.title,
            "description": report.description,
            "status": report.status,
            "content": report.content,
            "file_path": report.file_path,
            "file_format": report.file_format,
            "generated_at": report.generated_at.isoformat() if report.generated_at else None,
            "generated_by": report.generated_by,
            "metrics": report.metrics,
            "is_scheduled": report.is_scheduled,
            "schedule": report.schedule,
            "created_at": report.created_at.isoformat(),
            "updated_at": report.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.put(
    "/{report_id}",
    response_model=ReportResponse,
    summary="Update report",
)
async def update_report(
    report_id: str,
    request: ReportUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Update report details."""
    try:
        service = ReportService(session)
        report = await service.update(
            tenant_id=current_user.tenant_id,
            report_id=uuid.UUID(report_id),
            updates=request.model_dump(exclude_unset=True),
        )

        return {
            "id": str(report.id),
            "report_type": report.report_type,
            "scope": report.scope,
            "title": report.title,
            "description": report.description,
            "status": report.status,
            "content": report.content,
            "file_path": report.file_path,
            "file_format": report.file_format,
            "generated_at": report.generated_at.isoformat() if report.generated_at else None,
            "generated_by": report.generated_by,
            "metrics": report.metrics,
            "is_scheduled": report.is_scheduled,
            "schedule": report.schedule,
            "created_at": report.created_at.isoformat(),
            "updated_at": report.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete report",
)
async def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
):
    """Delete a report (soft delete)."""
    try:
        service = ReportService(session)
        await service.delete(
            tenant_id=current_user.tenant_id,
            report_id=uuid.UUID(report_id),
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.post(
    "/{report_id}/generate",
    response_model=ReportResponse,
    summary="Generate report",
)
async def generate_report(
    report_id: str,
    request: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Generate and populate a report with content."""
    try:
        service = ReportService(session)
        report = await service.generate_report(
            tenant_id=current_user.tenant_id,
            report_id=uuid.UUID(report_id),
            content=request.content,
            metrics=request.metrics,
        )

        return {
            "id": str(report.id),
            "report_type": report.report_type,
            "scope": report.scope,
            "title": report.title,
            "description": report.description,
            "status": report.status,
            "content": report.content,
            "file_path": report.file_path,
            "file_format": report.file_format,
            "generated_at": report.generated_at.isoformat() if report.generated_at else None,
            "generated_by": report.generated_by,
            "metrics": report.metrics,
            "is_scheduled": report.is_scheduled,
            "schedule": report.schedule,
            "created_at": report.created_at.isoformat(),
            "updated_at": report.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/{report_id}/export",
    response_model=ReportResponse,
    summary="Export report",
)
async def export_report(
    report_id: str,
    request: ReportExportRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Export a generated report to a file."""
    try:
        service = ReportService(session)
        report = await service.export_report(
            tenant_id=current_user.tenant_id,
            report_id=uuid.UUID(report_id),
            file_path=request.file_path,
        )

        return {
            "id": str(report.id),
            "report_type": report.report_type,
            "scope": report.scope,
            "title": report.title,
            "description": report.description,
            "status": report.status,
            "content": report.content,
            "file_path": report.file_path,
            "file_format": report.file_format,
            "generated_at": report.generated_at.isoformat() if report.generated_at else None,
            "generated_by": report.generated_by,
            "metrics": report.metrics,
            "is_scheduled": report.is_scheduled,
            "schedule": report.schedule,
            "created_at": report.created_at.isoformat(),
            "updated_at": report.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
