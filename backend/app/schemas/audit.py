"""
Audit log schemas for response validation.

These are read-only since audit logs are immutable.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    """Audit log entry response."""

    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: Optional[uuid.UUID]
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: uuid.UUID = Field(..., description="ID of resource affected")
    old_values: Optional[Dict[str, Any]] = Field(None, description="Previous values")
    new_values: Optional[Dict[str, Any]] = Field(None, description="New values")
    request_id: str = Field(..., description="Request correlation ID")
    ip_address: Optional[str]
    user_agent: Optional[str]
    status: str = Field(..., description="SUCCESS or FAILURE")
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AuditResourceTimeline(BaseModel):
    """Timeline of all changes to a resource."""

    resource_id: uuid.UUID
    resource_type: str
    entries: List[AuditLogResponse]


class AuditUserActivity(BaseModel):
    """Activity of a specific user."""

    user_id: uuid.UUID
    entries: List[AuditLogResponse]


class AuditFailedOperation(BaseModel):
    """Failed operation details for investigation."""

    audit_id: uuid.UUID
    action: str
    resource_type: str
    resource_id: uuid.UUID
    error_message: str
    timestamp: datetime
    request_id: str
