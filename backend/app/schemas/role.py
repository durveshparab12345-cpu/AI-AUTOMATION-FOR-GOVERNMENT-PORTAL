"""
Role and permission schemas for request/response validation.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    """Base permission info."""

    resource: str = Field(..., min_length=1, description="Resource type")
    action: str = Field(..., min_length=1, description="Action type")


class PermissionResponse(PermissionBase):
    """Permission response."""

    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    """Create role request."""

    name: str = Field(..., min_length=1, max_length=100, description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    permissions: List[PermissionBase] = Field(default=[], description="Initial permissions")


class RoleUpdate(BaseModel):
    """Update role request."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RoleResponse(BaseModel):
    """Role response."""

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: Optional[str]
    is_system: bool
    is_active: bool
    permissions: List[PermissionResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoleDetailResponse(RoleResponse):
    """Detailed role response with permission counts."""

    permission_count: int = Field(default=0, description="Number of permissions")


class GrantPermissionRequest(BaseModel):
    """Request to grant a permission to a role."""

    resource: str = Field(..., description="Resource type")
    action: str = Field(..., description="Action type")


class RevokePermissionRequest(BaseModel):
    """Request to revoke a permission from a role."""

    resource: str = Field(..., description="Resource type")
    action: str = Field(..., description="Action type")
