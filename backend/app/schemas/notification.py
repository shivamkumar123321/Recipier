"""
Notification-related Pydantic schemas for request/response validation.
"""

from typing import Any, Dict, List, Optional

from pydantic import Field

from app.schemas.base import BaseSchema, TimestampSchema


# Notification Schemas
class NotificationBase(BaseSchema):
    """Base notification schema."""

    notification_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Type of notification",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Notification title",
    )
    message: str = Field(
        ...,
        min_length=1,
        description="Notification message",
    )
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional data (item IDs, links, etc.)",
    )
    priority: str = Field(
        default="medium",
        pattern="^(low|medium|high|urgent)$",
        description="Priority level",
    )


class NotificationCreate(NotificationBase):
    """Schema for creating notification."""

    user_id: int = Field(..., description="User ID to send notification to")


class NotificationUpdate(BaseSchema):
    """Schema for updating notification."""

    is_read: Optional[bool] = None


class NotificationResponse(NotificationBase, TimestampSchema):
    """Schema for notification responses."""

    id: int
    user_id: int
    is_read: bool
    read_at: Optional[str] = None


class NotificationListResponse(BaseSchema):
    """Schema for paginated notification list."""

    items: List[NotificationResponse]
    total: int
    unread_count: int
    skip: int
    limit: int


class NotificationMarkReadRequest(BaseSchema):
    """Schema for marking notification as read."""

    is_read: bool = Field(default=True, description="Mark as read (true) or unread (false)")


class NotificationBulkMarkReadRequest(BaseSchema):
    """Schema for marking multiple notifications as read."""

    notification_ids: List[int] = Field(..., description="List of notification IDs to mark as read")
    is_read: bool = Field(default=True, description="Mark as read (true) or unread (false)")
