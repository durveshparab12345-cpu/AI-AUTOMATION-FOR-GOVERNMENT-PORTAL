"""
NotificationService — business logic for notification creation and management.

Handles:
- Notification CRUD operations
- Multi-channel delivery
- Read status tracking
- Retry logic
"""

from __future__ import annotations

import uuid
import logging
from typing import Any
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository
from app.core.constants import ErrorCode
from app.exceptions import APIException

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for notification creation and management."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session
        self.notification_repo = NotificationRepository(session)

    async def create(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str,
        message: str,
        notification_type: str = "INFO",
        channels: str = "IN_APP",
        action_url: str | None = None,
        action_label: str | None = None,
    ) -> Notification:
        """
        Create a new notification.

        Args:
            tenant_id: Organization ID
            user_id: Target user ID
            title: Notification title
            message: Notification message
            notification_type: Type (INFO, WARNING, ERROR, etc)
            channels: Delivery channels (IN_APP, EMAIL, SMS, PUSH)
            action_url: Optional action link
            action_label: Optional action label

        Returns:
            Created notification

        Raises:
            APIException: If creation fails
        """
        notification = await self.notification_repo.create({
            "user_id": user_id,
            "title": title,
            "message": message,
            "notification_type": notification_type,
            "channels": channels,
            "status": "PENDING",
            "action_url": action_url,
            "action_label": action_label,
            "retry_count": 0,
        })

        await self.session.commit()
        logger.info(
            f"Notification created: {notification.id} for user {user_id}"
        )
        return notification

    async def get(
        self,
        tenant_id: uuid.UUID,
        notification_id: uuid.UUID,
    ) -> Notification:
        """
        Get a notification by ID.

        Raises:
            APIException: If not found
        """
        notification = await self.notification_repo.read(notification_id)
        if not notification:
            raise APIException(
                error_code=ErrorCode.NOT_FOUND,
                message="Notification not found",
            )
        return notification

    async def list(
        self,
        tenant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        user_id: uuid.UUID | None = None,
        status: str | None = None,
        unread_only: bool = False,
    ) -> tuple[list[Notification], int]:
        """
        List notifications with optional filtering.

        Args:
            tenant_id: Organization ID
            skip: Pagination offset
            limit: Pagination limit
            user_id: Filter by user
            status: Filter by status
            unread_only: Only unread notifications

        Returns:
            Tuple of (notifications, total_count)
        """
        if user_id and unread_only:
            return await self.notification_repo.list_unread_by_user(
                user_id, skip, limit
            )

        if user_id:
            return await self.notification_repo.list_by_user(
                user_id, skip, limit
            )

        if status:
            return await self.notification_repo.list_by_status(status, skip, limit)

        return await self.notification_repo.list(
            skip=skip,
            limit=limit,
            order_by="created_at",
            order_desc=True,
        )

    async def update(
        self,
        tenant_id: uuid.UUID,
        notification_id: uuid.UUID,
        updates: dict[str, Any],
    ) -> Notification:
        """
        Update a notification.

        Args:
            tenant_id: Organization ID
            notification_id: Notification ID
            updates: Fields to update

        Returns:
            Updated notification

        Raises:
            APIException: If not found
        """
        notification = await self.get(tenant_id, notification_id)

        # Allow updating certain fields
        allowed_fields = {
            "message",
            "status",
            "error_message",
            "action_url",
            "action_label",
        }
        updates = {k: v for k, v in updates.items() if k in allowed_fields}

        if updates:
            notification = await self.notification_repo.update(
                notification_id, updates
            )

        await self.session.commit()
        logger.info(f"Notification updated: {notification_id}")
        return notification

    async def mark_as_read(
        self,
        tenant_id: uuid.UUID,
        notification_id: uuid.UUID,
    ) -> Notification:
        """
        Mark a notification as read.

        Args:
            tenant_id: Organization ID
            notification_id: Notification ID

        Returns:
            Updated notification
        """
        notification = await self.get(tenant_id, notification_id)

        updates = {
            "status": "READ",
            "read_at": datetime.now(timezone.utc),
        }

        notification = await self.notification_repo.update(
            notification_id, updates
        )
        await self.session.commit()

        logger.info(f"Notification marked as read: {notification_id}")
        return notification

    async def mark_as_sent(
        self,
        tenant_id: uuid.UUID,
        notification_id: uuid.UUID,
    ) -> Notification:
        """
        Mark a notification as sent.

        Args:
            tenant_id: Organization ID
            notification_id: Notification ID

        Returns:
            Updated notification
        """
        notification = await self.get(tenant_id, notification_id)

        updates = {
            "status": "SENT",
            "sent_at": datetime.now(timezone.utc),
        }

        notification = await self.notification_repo.update(
            notification_id, updates
        )
        await self.session.commit()

        logger.info(f"Notification marked as sent: {notification_id}")
        return notification

    async def mark_as_delivered(
        self,
        tenant_id: uuid.UUID,
        notification_id: uuid.UUID,
    ) -> Notification:
        """
        Mark a notification as delivered.

        Args:
            tenant_id: Organization ID
            notification_id: Notification ID

        Returns:
            Updated notification
        """
        notification = await self.get(tenant_id, notification_id)

        updates = {
            "status": "DELIVERED",
            "delivered_at": datetime.now(timezone.utc),
        }

        notification = await self.notification_repo.update(
            notification_id, updates
        )
        await self.session.commit()

        logger.info(f"Notification marked as delivered: {notification_id}")
        return notification

    async def mark_as_failed(
        self,
        tenant_id: uuid.UUID,
        notification_id: uuid.UUID,
        error_message: str | None = None,
    ) -> Notification:
        """
        Mark a notification as failed.

        Args:
            tenant_id: Organization ID
            notification_id: Notification ID
            error_message: Failure reason

        Returns:
            Updated notification
        """
        notification = await self.get(tenant_id, notification_id)

        updates = {
            "status": "FAILED",
            "error_message": error_message,
        }

        notification = await self.notification_repo.update(
            notification_id, updates
        )
        await self.session.commit()

        logger.info(f"Notification marked as failed: {notification_id}")
        return notification

    async def delete(
        self,
        tenant_id: uuid.UUID,
        notification_id: uuid.UUID,
    ) -> bool:
        """
        Delete a notification (soft delete).

        Args:
            tenant_id: Organization ID
            notification_id: Notification ID

        Returns:
            True if deleted

        Raises:
            APIException: If not found
        """
        notification = await self.get(tenant_id, notification_id)

        # Mark as deleted
        notification.mark_deleted(uuid.UUID(int=0))

        await self.session.commit()
        logger.info(f"Notification deleted: {notification_id}")
        return True
