"""
Notification model for user notifications.

Stores notifications for users about expiring items, meal plans, etc.
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Notification(Base, TimestampMixin):
    """
    User notifications for various events.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        notification_type: Type of notification (expiring_item, meal_plan_ready, etc.)
        title: Notification title
        message: Notification message
        data: Additional data (JSONB) - e.g., item IDs, links
        is_read: Whether the notification has been read
        read_at: Timestamp when notification was read
        priority: Priority level (low, medium, high, urgent)
    """

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who receives the notification",
    )
    notification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Type of notification",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Notification title",
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Notification message",
    )
    data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional data (item IDs, links, etc.)",
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether notification has been read",
    )
    read_at: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Timestamp when notification was read",
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        default="medium",
        nullable=False,
        comment="Priority level (low, medium, high, urgent)",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type='{self.notification_type}', user_id={self.user_id}, read={self.is_read})>"
