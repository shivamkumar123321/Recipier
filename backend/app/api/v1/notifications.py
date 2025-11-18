"""
Notification API endpoints.

Provides endpoints for managing user notifications.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.logging import get_logger
from app.models.user import User
from app.schemas.notification import (
    NotificationBulkMarkReadRequest,
    NotificationListResponse,
    NotificationMarkReadRequest,
    NotificationResponse,
)
from app.services.notification_service import notification_service

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    unread_only: bool = Query(False, description="Filter to only unread notifications"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get user's notifications with optional filtering.

    Filters:
    - **unread_only**: Show only unread notifications (default: false)

    Pagination:
    - **skip**: Number of records to skip (offset)
    - **limit**: Maximum number of records to return (max: 100)

    Returns:
    - List of notifications
    - Total count
    - Unread count
    """
    logger.info(
        f"Get notifications request from user {current_user.id}, "
        f"unread_only={unread_only}"
    )

    notifications, total, unread_count = await notification_service.get_user_notifications(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
    )

    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        unread_count=unread_count,
        skip=skip,
        limit=limit,
    )


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: int,
    request: NotificationMarkReadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Mark a notification as read or unread.

    Request body:
    - **is_read**: Mark as read (true) or unread (false) - default: true

    Returns updated notification.
    """
    logger.info(
        f"Mark notification {notification_id} as "
        f"{'read' if request.is_read else 'unread'} for user {current_user.id}"
    )

    notification = await notification_service.mark_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id,
        is_read=request.is_read,
    )

    return NotificationResponse.model_validate(notification)


@router.post("/mark-all-read", status_code=status.HTTP_200_OK)
async def mark_all_notifications_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Mark all notifications for the current user as read.

    Returns:
    - Number of notifications marked as read
    """
    logger.info(f"Mark all notifications as read for user {current_user.id}")

    count = await notification_service.mark_all_as_read(
        db=db,
        user_id=current_user.id,
    )

    return {
        "count": count,
        "message": f"Marked {count} notifications as read",
    }


@router.post("/bulk-mark-read", status_code=status.HTTP_200_OK)
async def bulk_mark_notifications_as_read(
    request: NotificationBulkMarkReadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Mark multiple notifications as read or unread.

    Request body:
    - **notification_ids**: List of notification IDs to update
    - **is_read**: Mark as read (true) or unread (false) - default: true

    Returns:
    - Number of notifications updated
    """
    logger.info(
        f"Bulk mark {len(request.notification_ids)} notifications as "
        f"{'read' if request.is_read else 'unread'} for user {current_user.id}"
    )

    count = await notification_service.bulk_mark_as_read(
        db=db,
        notification_ids=request.notification_ids,
        user_id=current_user.id,
        is_read=request.is_read,
    )

    return {
        "count": count,
        "message": f"Marked {count} notifications as {'read' if request.is_read else 'unread'}",
    }


@router.get("/unread-count", status_code=status.HTTP_200_OK)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get count of unread notifications for the current user.

    Returns:
    - Unread notification count
    """
    _, _, unread_count = await notification_service.get_user_notifications(
        db=db,
        user_id=current_user.id,
        skip=0,
        limit=1,  # We only need the count
    )

    return {
        "unread_count": unread_count,
    }
