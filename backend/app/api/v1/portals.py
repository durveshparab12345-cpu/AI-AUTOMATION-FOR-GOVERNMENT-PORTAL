"""
API endpoints for portal management.

Endpoints:
    POST   /api/v1/portals         - Create portal
    GET    /api/v1/portals         - List portals
    GET    /api/v1/portals/{id}    - Get portal
    PUT    /api/v1/portals/{id}    - Update portal
    DELETE /api/v1/portals/{id}    - Delete portal
    POST   /api/v1/portals/{id}/activate   - Activate portal
    POST   /api/v1/portals/{id}/deactivate - Deactivate portal
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.core.dependencies import get_current_user
from app.services.portal_service import PortalService
from app.models.user import User
from app.core.constants import PortalStatus, PortalType

router = APIRouter(prefix="/portals", tags=["portals"])


# ============================================================================
# SCHEMAS
# ============================================================================

class PortalCreateRequest(BaseModel):
    """Request schema for creating a portal."""

    name: str = Field(..., min_length=1, max_length=255)
    base_url: str = Field(..., min_length=1, max_length=500)
    type: str = Field(default="CUSTOM", max_length=50)
    auth_type: str = Field(default="BASIC", max_length=50)
    description: str | None = Field(None, max_length=2000)


class PortalUpdateRequest(BaseModel):
    """Request schema for updating a portal."""

    name: str | None = Field(None, min_length=1, max_length=255)
    base_url: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = Field(None, max_length=2000)


class PortalResponse(BaseModel):
    """Response schema for portal."""

    id: str
    name: str
    description: str | None
    type: str
    base_url: str
    auth_type: str
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class PortalListResponse(BaseModel):
    """Response schema for portal list."""

    items: list[PortalResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "",
    response_model=PortalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create portal",
)
async def create_portal(
    request: PortalCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Create a new portal configuration."""
    try:
        service = PortalService(session)
        portal = await service.create_portal(
            organization_id=current_user.tenant_id,
            name=request.name,
            base_url=request.base_url,
            portal_type=request.type,
            auth_type=request.auth_type,
            description=request.description,
            created_by=current_user.id,
        )

        return {
            "id": str(portal.id),
            "name": portal.name,
            "description": portal.description,
            "type": portal.type.value if hasattr(portal.type, "value") else portal.type,
            "base_url": portal.base_url,
            "auth_type": portal.auth_type,
            "status": portal.status.value if hasattr(portal.status, "value") else portal.status,
            "created_at": portal.created_at.isoformat(),
            "updated_at": portal.updated_at.isoformat(),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=PortalListResponse,
    summary="List portals",
)
async def list_portals(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """List portals for the organization."""
    try:
        service = PortalService(session)
        
        # Convert status string to enum if provided
        status_enum = None
        if status:
            try:
                status_enum = PortalStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status}",
                )

        portals, total = await service.list_portals(
            organization_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            status=status_enum,
        )

        items = [
            {
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "type": p.type.value if hasattr(p.type, "value") else p.type,
                "base_url": p.base_url,
                "auth_type": p.auth_type,
                "status": p.status.value if hasattr(p.status, "value") else p.status,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat(),
            }
            for p in portals
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
    "/{portal_id}",
    response_model=PortalResponse,
    summary="Get portal",
)
async def get_portal(
    portal_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Get portal details."""
    try:
        service = PortalService(session)
        portal = await service.get_portal(
            portal_id=uuid.UUID(portal_id),
            organization_id=current_user.tenant_id,
        )

        return {
            "id": str(portal.id),
            "name": portal.name,
            "description": portal.description,
            "type": portal.type.value if hasattr(portal.type, "value") else portal.type,
            "base_url": portal.base_url,
            "auth_type": portal.auth_type,
            "status": portal.status.value if hasattr(portal.status, "value") else portal.status,
            "created_at": portal.created_at.isoformat(),
            "updated_at": portal.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid portal ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.put(
    "/{portal_id}",
    response_model=PortalResponse,
    summary="Update portal",
)
async def update_portal(
    portal_id: str,
    request: PortalUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Update portal details."""
    try:
        service = PortalService(session)
        portal = await service.update_portal(
            portal_id=uuid.UUID(portal_id),
            organization_id=current_user.tenant_id,
            updates=request.model_dump(exclude_unset=True),
            updated_by=current_user.id,
        )

        return {
            "id": str(portal.id),
            "name": portal.name,
            "description": portal.description,
            "type": portal.type.value if hasattr(portal.type, "value") else portal.type,
            "base_url": portal.base_url,
            "auth_type": portal.auth_type,
            "status": portal.status.value if hasattr(portal.status, "value") else portal.status,
            "created_at": portal.created_at.isoformat(),
            "updated_at": portal.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid portal ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/{portal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete portal",
)
async def delete_portal(
    portal_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
):
    """Delete a portal (soft delete)."""
    try:
        service = PortalService(session)
        await service.delete_portal(
            portal_id=uuid.UUID(portal_id),
            organization_id=current_user.tenant_id,
            deleted_by=current_user.id,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid portal ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.post(
    "/{portal_id}/activate",
    response_model=PortalResponse,
    summary="Activate portal",
)
async def activate_portal(
    portal_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Activate a portal."""
    try:
        service = PortalService(session)
        portal = await service.activate_portal(
            portal_id=uuid.UUID(portal_id),
            organization_id=current_user.tenant_id,
            updated_by=current_user.id,
        )

        return {
            "id": str(portal.id),
            "name": portal.name,
            "description": portal.description,
            "type": portal.type.value if hasattr(portal.type, "value") else portal.type,
            "base_url": portal.base_url,
            "auth_type": portal.auth_type,
            "status": portal.status.value if hasattr(portal.status, "value") else portal.status,
            "created_at": portal.created_at.isoformat(),
            "updated_at": portal.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid portal ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/{portal_id}/deactivate",
    response_model=PortalResponse,
    summary="Deactivate portal",
)
async def deactivate_portal(
    portal_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Deactivate a portal."""
    try:
        service = PortalService(session)
        portal = await service.deactivate_portal(
            portal_id=uuid.UUID(portal_id),
            organization_id=current_user.tenant_id,
            updated_by=current_user.id,
        )

        return {
            "id": str(portal.id),
            "name": portal.name,
            "description": portal.description,
            "type": portal.type.value if hasattr(portal.type, "value") else portal.type,
            "base_url": portal.base_url,
            "auth_type": portal.auth_type,
            "status": portal.status.value if hasattr(portal.status, "value") else portal.status,
            "created_at": portal.created_at.isoformat(),
            "updated_at": portal.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid portal ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
