"""
API endpoints for notification management.

Endpoints:
    POST   /api/v1/notifications              - Create notification
    GET    /api/v1/notifications              - List notifications
    GET    /api/v1/notifications/{id}         - Get notification
    PUT    /api/v1/notifications/{id}         - Update notification
    DELETE /api/v1/notifications/{id}         - Delete notification
    POST   /api/v1/notifications/{id}/read    - Mark as read
    GET    /api/v1/notifications/user/{user_id} - List by user
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.core.dependencies import get_current_user
from app.services.notification_service import NotificationService
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["notifications"])


# ============================================================================
# SCHEMAS
# ============================================================================

class NotificationCreateRequest(BaseModel):
    """Request schema for creating a notification."""

    user_id: uuid.UUID = Field(..., description="Target user ID")
    title: str = Field(..., min_length=1, max_length=255, description="Notification title")
    message: str = Field(..., min_length=1, description="Notification message")
    notification_type: str = Field(default="INFO", max_length=50, description="Notification type")
    channels: str = Field(default="IN_APP", max_length=100, description="Delivery channels")
    action_url: str | None = Field(None, max_length=500, description="Action link")
    action_label: str | None = Field(None, max_length=100, description="Action label")


class NotificationUpdateRequest(BaseModel):
    """Request schema for updating a notification."""

    title: str | None = Field(None, min_length=1, max_length=255)
    message: str | None = Field(None, min_length=1)
    status: str | None = Field(None, max_length=50)
    action_url: str | None = Field(None, max_length=500)
    action_label: str | None = Field(None, max_length=100)


class NotificationResponse(BaseModel):
    """Response schema for notification."""

    id: str
    user_id: str
    title: str
    message: str
    notification_type: str
    status: str
    channels: str
    action_url: str | None
    action_label: str | None
    sent_at: str | None
    delivered_at: str | None
    read_at: str | None
    error_message: str | None
    retry_count: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Response schema for notification list."""

    items: list[NotificationResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create notification",
)
async def create_notification(
    request: NotificationCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Create a new notification."""
    try:
        service = NotificationService(session)
        notification = await service.create(
            tenant_id=current_user.tenant_id,
            user_id=request.user_id,
            title=request.title,
            message=request.message,
            notification_type=request.notification_type,
            channels=request.channels,
            action_url=request.action_url,
            action_label=request.action_label,
        )

        return {
            "id": str(notification.id),
            "user_id": str(notification.user_id),
            "title": notification.title,
            "message": notification.message,
            "notification_type": notification.notification_type,
            "status": notification.status,
            "channels": notification.channels,
            "action_url": notification.action_url,
            "action_label": notification.action_label,
            "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
            "delivered_at": notification.delivered_at.isoformat() if notification.delivered_at else None,
            "read_at": notification.read_at.isoformat() if notification.read_at else None,
            "error_message": notification.error_message,
            "retry_count": notification.retry_count,
            "created_at": notification.created_at.isoformat(),
            "updated_at": notification.updated_at.isoformat(),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="List notifications",
)
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """List notifications for the organization."""
    try:
        service = NotificationService(session)
        notifications, total = await service.list(
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            user_id=user_id,
            status=status,
            unread_only=unread_only,
        )

        items = [
            {
                "id": str(n.id),
                "user_id": str(n.user_id),
                "title": n.title,
                "message": n.message,
                "notification_type": n.notification_type,
                "status": n.status,
                "channels": n.channels,
                "action_url": n.action_url,
                "action_label": n.action_label,
                "sent_at": n.sent_at.isoformat() if n.sent_at else None,
                "delivered_at": n.delivered_at.isoformat() if n.delivered_at else None,
                "read_at": n.read_at.isoformat() if n.read_at else None,
                "error_message": n.error_message,
                "retry_count": n.retry_count,
                "created_at": n.created_at.isoformat(),
                "updated_at": n.updated_at.isoformat(),
            }
            for n in notifications
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
    "/{notification_id}",
    response_model=NotificationResponse,
    summary="Get notification",
)
async def get_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Get notification details."""
    try:
        service = NotificationService(session)
        notification = await service.get(
            tenant_id=current_user.tenant_id,
            notification_id=uuid.UUID(notification_id),
        )

        return {
            "id": str(notification.id),
            "user_id": str(notification.user_id),
            "title": notification.title,
            "message": notification.message,
            "notification_type": notification.notification_type,
            "status": notification.status,
            "channels": notification.channels,
            "action_url": notification.action_url,
            "action_label": notification.action_label,
            "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
            "delivered_at": notification.delivered_at.isoformat() if notification.delivered_at else None,
            "read_at": notification.read_at.isoformat() if notification.read_at else None,
            "error_message": notification.error_message,
            "retry_count": notification.retry_count,
            "created_at": notification.created_at.isoformat(),
            "updated_at": notification.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.put(
    "/{notification_id}",
    response_model=NotificationResponse,
    summary="Update notification",
)
async def update_notification(
    notification_id: str,
    request: NotificationUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Update notification details."""
    try:
        service = NotificationService(session)
        notification = await service.update(
            tenant_id=current_user.tenant_id,
            notification_id=uuid.UUID(notification_id),
            updates=request.model_dump(exclude_unset=True),
        )

        return {
            "id": str(notification.id),
            "user_id": str(notification.user_id),
            "title": notification.title,
            "message": notification.message,
            "notification_type": notification.notification_type,
            "status": notification.status,
            "channels": notification.channels,
            "action_url": notification.action_url,
            "action_label": notification.action_label,
            "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
            "delivered_at": notification.delivered_at.isoformat() if notification.delivered_at else None,
            "read_at": notification.read_at.isoformat() if notification.read_at else None,
            "error_message": notification.error_message,
            "retry_count": notification.retry_count,
            "created_at": notification.created_at.isoformat(),
            "updated_at": notification.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete notification",
)
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
):
    """Delete a notification (soft delete)."""
    try:
        service = NotificationService(session)
        await service.delete(
            tenant_id=current_user.tenant_id,
            notification_id=uuid.UUID(notification_id),
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.post(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark notification as read",
)
async def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(AsyncSessionLocal),
) -> dict[str, Any]:
    """Mark a notification as read."""
    try:
        service = NotificationService(session)
        notification = await service.mark_as_read(
            tenant_id=current_user.tenant_id,
            notification_id=uuid.UUID(notification_id),
        )

        return {
            "id": str(notification.id),
            "user_id": str(notification.user_id),
            "title": notification.title,
            "message": notification.message,
            "notification_type": notification.notification_type,
            "status": notification.status,
            "channels": notification.channels,
            "action_url": notification.action_url,
            "action_label": notification.action_label,
            "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
            "delivered_at": notification.delivered_at.isoformat() if notification.delivered_at else None,
            "read_at": notification.read_at.isoformat() if notification.read_at else None,
            "error_message": notification.error_message,
            "retry_count": notification.retry_count,
            "created_at": notification.created_at.isoformat(),
            "updated_at": notification.updated_at.isoformat(),
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
