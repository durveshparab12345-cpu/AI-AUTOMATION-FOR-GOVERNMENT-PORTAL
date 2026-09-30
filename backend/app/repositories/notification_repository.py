"""
NotificationRepository — data access for Notification model.

Handles notification-specific queries including status and read tracking.
"""

from __future__ import annotations

import uuid

from sqlalchemy import and_, select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """Repository for Notification model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Notification)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Notification], int]:
        """List all notifications for a user."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        notifications = result.scalars().all()

        return notifications, total

    async def list_unread_by_user(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Notification], int]:
        """List all unread notifications for a user."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Notification.id)).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.status != "READ",
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Notification)
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.status != "READ",
                )
            )
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        notifications = result.scalars().all()

        return notifications, total

    async def list_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Notification], int]:
        """List all notifications with a specific status."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Notification.id)).where(
                Notification.status == status
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Notification)
            .where(Notification.status == status)
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        notifications = result.scalars().all()

        return notifications, total
