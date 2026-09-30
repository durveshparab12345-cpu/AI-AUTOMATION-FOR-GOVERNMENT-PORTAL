"""
Notification model — in-app and external notifications.

Tracks notifications sent to users via various channels (in-app, email, SMS, etc).
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Text, Enum as SQLEnum, ForeignKey, Index, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class Notification(BaseModel):
    """
    Notification to a user.
    
    Tracks notifications via multiple channels: in-app, email, SMS, etc.
    Supports read status, retry logic, and delivery tracking.
    """

    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_user_id", "user_id"),
        Index("ix_notifications_status", "status"),
        Index("ix_notifications_type", "notification_type"),
    )

    # References
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Type & channel
    notification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="INFO",  # INFO, WARNING, ERROR, SUCCESS, ACTION_REQUIRED
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING",  # PENDING, SENT, DELIVERED, FAILED, READ
    )

    # Channels
    channels: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="IN_APP",  # IN_APP, EMAIL, SMS, PUSH
    )

    # Delivery tracking
    sent_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Error tracking
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(default=0)

    # Action link
    action_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    action_label: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    user: Mapped[User] = relationship(
        "User",
        foreign_keys=[user_id],
        primaryjoin="Notification.user_id == User.id",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Notification(id={self.id}, title={self.title}, status={self.status})>"

    @property
    def is_read(self) -> bool:
        """Check if notification has been read."""
        return self.status == "READ"

    @property
    def is_sent(self) -> bool:
        """Check if notification has been sent."""
        return self.status in ("SENT", "DELIVERED", "READ")

    @property
    def is_failed(self) -> bool:
        """Check if notification failed to send."""
        return self.status == "FAILED"

    @property
    def can_retry(self) -> bool:
        """Check if notification can be retried."""
        return self.status in ("PENDING", "FAILED") and self.retry_count < 3
