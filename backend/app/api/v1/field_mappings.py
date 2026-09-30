"""
API endpoints for field mapping management.

Endpoints:
    POST   /api/v1/field_mappings                - Create field mapping
    GET    /api/v1/field_mappings                - List field mappings
    GET    /api/v1/field_mappings/{id}           - Get field mapping
    PUT    /api/v1/field_mappings/{id}           - Update field mapping
    DELETE /api/v1/field_mappings/{id}           - Delete field mapping
    POST   /api/v1/field_mappings/{id}/validate  - Validate field value
    POST   /api/v1/field_mappings/{id}/transform - Transform field value
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.core.dependencies import get_current_user
from app.services.field_mapping_service import FieldMappingService
from app.models.user import User

router = APIRouter(prefix="/field_mappings", tags=["field_mappings"])


# ============================================================================
# SCHEMAS
# ============================================================================

class FieldMappingCreateRequest(BaseModel):
    """Request schema for creating a field mapping."""

    workflow_id: uuid.UUID = Field(..., description="Associated workflow ID")
    portal_field: str = Field(..., min_length=1, max_length=255, description="Portal field name")
    system_field: str = Field(..., min_length=1, max_length=255, description="System field name")
    mapping_type: str = Field(default="DIRECT", max_length=50, description="Mapping type")
    direction: str = Field(default="BIDIRECTIONAL", max_length=50, description="Mapping direction")
    transformation_logic: str | None = Field(None, description="Transformation logic")
    validation_rules: str | None = Field(None, description="Validation rules (JSON)")
    is_required: bool = Field(default=False, description="Whether field is required")
    description: str | None = Field(None, description="Mapping description")


class FieldMappingUpdateRequest(BaseModel):
    """Request schema for updating a field mapping."""

    mapping_type: str | None = Field(None, max_length=50)
    direction: str | None = Field(None, max_length=50)
    transformation_logic: str | None = Field(None)
    validation_rules: str | None = Field(None)
    is_required: bool | None = Field(None)
    description: str | None = Field(None)


class FieldMappingValidateRequest(BaseModel):
    """Request schema for validating a field value."""

    value: Any = Field(..., description="Value to validate")


class FieldMappingTransformRequest(BaseModel):
    """Request schema for transforming a field value."""

    value: Any = Field(..., description="Value to transform")
    direction: str = Field(default="output", description="Transform direction (input/output)")


class FieldMappingResponse(BaseModel):
    """Response schema for field mapping."""

    id: str
    workflow_id: str
    portal_field: str
    system_field: str
    mapping_type: str
    direction: str
    transformation_logic: str | None
    validation_rules: str | None
    is_required: bool
    description: str | None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class FieldMappingListResponse(BaseModel):
    """Response schema for field mapping list."""

    items: list[FieldMappingResponse]
    total: int
    skip: int
    limit: int


class FieldMappingValidateResponse(BaseModel):
    """Response schema for validation result."""

    is_valid: bool
    message: str | None = None


class FieldMappingTransformResponse(BaseModel):
    """Response schema for transformation result."""

    transformed_value: Any
    message: str | None = None


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "",
    response_model=FieldMappingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create field mapping",
)
async def create_field_mapping(
    request: FieldMappingCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Create a new field mapping."""
    try:
        service = FieldMappingService(session)
        mapping = await service.create(
            tenant_id=current_user.tenant_id,
            workflow_id=request.workflow_id,
            portal_field=request.portal_field,
            system_field=request.system_field,
            mapping_type=request.mapping_type,
            direction=request.direction,
            transformation_logic=request.transformation_logic,
            validation_rules=request.validation_rules,
            is_required=request.is_required,
            description=request.description,
        )

        return {
            "id": str(mapping.id),
            "workflow_id": str(mapping.workflow_id),
            "portal_field": mapping.portal_field,
            "system_field": mapping.system_field,
            "mapping_type": mapping.mapping_type,
            "direction": mapping.direction,
            "transformation_logic": mapping.transformation_logic,
            "validation_rules": mapping.validation_rules,
            "is_required": mapping.is_required,
            "description": mapping.description,
            "created_at": mapping.created_at.isoformat(),
            "updated_at": mapping.updated_at.isoformat(),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=FieldMappingListResponse,
    summary="List field mappings",
)
async def list_field_mappings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    workflow_id: uuid.UUID | None = Query(None),
    mapping_type: str | None = Query(None),
    required_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """List field mappings for the organization."""
    try:
        service = FieldMappingService(session)
        mappings, total = await service.list(
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            workflow_id=workflow_id,
            mapping_type=mapping_type,
            required_only=required_only,
        )

        items = [
            {
                "id": str(m.id),
                "workflow_id": str(m.workflow_id),
                "portal_field": m.portal_field,
                "system_field": m.system_field,
                "mapping_type": m.mapping_type,
                "direction": m.direction,
                "transformation_logic": m.transformation_logic,
                "validation_rules": m.validation_rules,
                "is_required": m.is_required,
                "description": m.description,
                "created_at": m.created_at.isoformat(),
                "updated_at": m.updated_at.isoformat(),
            }
            for m in mappings
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
    "/{mapping_id}",
    response_model=FieldMappingResponse,
    summary="Get field mapping",
)
async def get_field_mapping(
    mapping_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Get field mapping details."""
    try:
        service = FieldMappingService(session)
        mapping = await service.get(
            tenant_id=current_user.tenant_id,
            mapping_id=uuid.UUID(mapping_id),
        )

        return {
            "id": str(mapping.id),
            "workflow_id": str(mapping.workflow_id),
            "portal_field": mapping.portal_field,
            "system_field": mapping.system_field,
            "mapping_type": mapping.mapping_type,
            "direction": mapping.direction,
            "transformation_logic": mapping.transformation_logic,
            "validation_rules": mapping.validation_rules,
            "is_required": mapping.is_required,
            "description": mapping.description,
            "created_at": mapping.created_at.isoformat(),
            "updated_at": mapping.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mapping ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.put(
    "/{mapping_id}",
    response_model=FieldMappingResponse,
    summary="Update field mapping",
)
async def update_field_mapping(
    mapping_id: str,
    request: FieldMappingUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Update field mapping details."""
    try:
        service = FieldMappingService(session)
        mapping = await service.update(
            tenant_id=current_user.tenant_id,
            mapping_id=uuid.UUID(mapping_id),
            updates=request.model_dump(exclude_unset=True),
        )

        return {
            "id": str(mapping.id),
            "workflow_id": str(mapping.workflow_id),
            "portal_field": mapping.portal_field,
            "system_field": mapping.system_field,
            "mapping_type": mapping.mapping_type,
            "direction": mapping.direction,
            "transformation_logic": mapping.transformation_logic,
            "validation_rules": mapping.validation_rules,
            "is_required": mapping.is_required,
            "description": mapping.description,
            "created_at": mapping.created_at.isoformat(),
            "updated_at": mapping.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mapping ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/{mapping_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete field mapping",
)
async def delete_field_mapping(
    mapping_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
):
    """Delete a field mapping (soft delete)."""
    try:
        service = FieldMappingService(session)
        await service.delete(
            tenant_id=current_user.tenant_id,
            mapping_id=uuid.UUID(mapping_id),
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mapping ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.post(
    "/{mapping_id}/validate",
    response_model=FieldMappingValidateResponse,
    summary="Validate field value",
)
async def validate_field_value(
    mapping_id: str,
    request: FieldMappingValidateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Validate a field value against mapping rules."""
    try:
        service = FieldMappingService(session)
        is_valid = await service.validate_mapping(
            tenant_id=current_user.tenant_id,
            mapping_id=uuid.UUID(mapping_id),
            value=request.value,
        )

        return {
            "is_valid": is_valid,
            "message": "Validation passed" if is_valid else None,
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mapping ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/{mapping_id}/transform",
    response_model=FieldMappingTransformResponse,
    summary="Transform field value",
)
async def transform_field_value(
    mapping_id: str,
    request: FieldMappingTransformRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Transform a field value using the mapping's transformation logic."""
    try:
        service = FieldMappingService(session)
        transformed = await service.transform_value(
            tenant_id=current_user.tenant_id,
            mapping_id=uuid.UUID(mapping_id),
            value=request.value,
            direction=request.direction,
        )

        return {
            "transformed_value": transformed,
            "message": "Transformation completed",
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mapping ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
