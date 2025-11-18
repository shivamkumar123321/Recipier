"""
Notification service for managing user notifications.

Handles notification creation, retrieval, and push notification sending.
"""

from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.notification import Notification
from app.repositories.notification_repository import notification_repository

logger = get_logger(__name__)


class NotificationService:
    """Service for notification operations."""

    async def create_notification(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        priority: str = "medium",
    ) -> Notification:
        """
        Create a new notification for a user.

        Args:
            db: Database session
            user_id: User ID
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            data: Additional data (item IDs, links, etc.)
            priority: Priority level (low, medium, high, urgent)

        Returns:
            Created notification
        """
        logger.info(
            f"Creating notification for user {user_id}: "
            f"type={notification_type}, priority={priority}"
        )

        notification_data = {
            "user_id": user_id,
            "notification_type": notification_type,
            "title": title,
            "message": message,
            "data": data,
            "priority": priority,
            "is_read": False,
        }

        notification = await notification_repository.create(db, notification_data)
        await db.commit()
        await db.refresh(notification)

        # PLACEHOLDER: Push notification to user's device
        # In production, integrate with:
        # - Firebase Cloud Messaging (FCM) for mobile push
        # - WebSocket for real-time browser notifications
        # - Email for high-priority notifications
        await self._send_push_notification(notification)

        logger.info(f"Notification created: {notification.id}")
        return notification

    async def get_user_notifications(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        unread_only: bool = False,
    ) -> Tuple[List[Notification], int, int]:
        """
        Get notifications for a user.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            unread_only: Filter to only unread notifications

        Returns:
            Tuple of (notifications list, total count, unread count)
        """
        logger.info(f"Fetching notifications for user {user_id}, unread_only={unread_only}")

        notifications, total, unread_count = await notification_repository.get_by_user(
            db, user_id, skip, limit, unread_only
        )

        logger.info(
            f"Found {total} notifications ({unread_count} unread) for user {user_id}"
        )
        return notifications, total, unread_count

    async def mark_as_read(
        self,
        db: AsyncSession,
        notification_id: int,
        user_id: int,
        is_read: bool = True,
    ) -> Notification:
        """
        Mark notification as read or unread.

        Args:
            db: Database session
            notification_id: Notification ID
            user_id: User ID
            is_read: Whether to mark as read (True) or unread (False)

        Returns:
            Updated notification

        Raises:
            HTTPException: If notification not found or access denied
        """
        logger.info(
            f"Marking notification {notification_id} as "
            f"{'read' if is_read else 'unread'} for user {user_id}"
        )

        # Verify ownership
        notification = await notification_repository.get_by_id_and_user(
            db, notification_id, user_id
        )

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )

        # Mark as read
        notification = await notification_repository.mark_as_read(
            db, notification_id, is_read
        )

        await db.commit()
        await db.refresh(notification)

        logger.info(f"Notification {notification_id} marked as {'read' if is_read else 'unread'}")
        return notification

    async def mark_all_as_read(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> int:
        """
        Mark all notifications for a user as read.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Number of notifications marked as read
        """
        logger.info(f"Marking all notifications as read for user {user_id}")

        count = await notification_repository.mark_all_as_read(db, user_id)

        await db.commit()

        logger.info(f"Marked {count} notifications as read for user {user_id}")
        return count

    async def bulk_mark_as_read(
        self,
        db: AsyncSession,
        notification_ids: List[int],
        user_id: int,
        is_read: bool = True,
    ) -> int:
        """
        Mark multiple notifications as read or unread.

        Args:
            db: Database session
            notification_ids: List of notification IDs
            user_id: User ID (for ownership verification)
            is_read: Whether to mark as read (True) or unread (False)

        Returns:
            Number of notifications updated
        """
        logger.info(
            f"Bulk marking {len(notification_ids)} notifications as "
            f"{'read' if is_read else 'unread'} for user {user_id}"
        )

        count = await notification_repository.bulk_mark_as_read(
            db, notification_ids, user_id, is_read
        )

        await db.commit()

        logger.info(f"Marked {count} notifications as {'read' if is_read else 'unread'}")
        return count

    async def send_expiring_items_notification(
        self,
        db: AsyncSession,
        user_id: int,
        expiring_items: List[Dict[str, Any]],
    ) -> Notification:
        """
        Send notification about expiring inventory items.

        Args:
            db: Database session
            user_id: User ID
            expiring_items: List of expiring items with details

        Returns:
            Created notification
        """
        item_count = len(expiring_items)

        if item_count == 0:
            logger.debug(f"No expiring items for user {user_id}, skipping notification")
            return None

        # Build notification message
        if item_count == 1:
            item = expiring_items[0]
            title = "Item Expiring Soon!"
            message = f"{item['name']} will expire on {item['expiration_date']}."
        else:
            title = f"{item_count} Items Expiring Soon!"
            item_names = ", ".join([item["name"] for item in expiring_items[:3]])
            if item_count > 3:
                item_names += f" and {item_count - 3} more"
            message = f"You have {item_count} items expiring soon: {item_names}."

        # Create notification
        notification = await self.create_notification(
            db=db,
            user_id=user_id,
            notification_type="expiring_items",
            title=title,
            message=message,
            data={
                "item_count": item_count,
                "items": expiring_items,
            },
            priority="high",
        )

        return notification

    async def send_meal_plan_ready_notification(
        self,
        db: AsyncSession,
        user_id: int,
        meal_plan_id: int,
        meal_plan_name: str,
    ) -> Notification:
        """
        Send notification when AI meal plan generation is complete.

        Args:
            db: Database session
            user_id: User ID
            meal_plan_id: Meal plan ID
            meal_plan_name: Meal plan name

        Returns:
            Created notification
        """
        notification = await self.create_notification(
            db=db,
            user_id=user_id,
            notification_type="meal_plan_ready",
            title="Meal Plan Ready!",
            message=f"Your meal plan '{meal_plan_name}' has been generated and is ready to view.",
            data={
                "meal_plan_id": meal_plan_id,
                "meal_plan_name": meal_plan_name,
            },
            priority="medium",
        )

        return notification

    async def send_grocery_list_ready_notification(
        self,
        db: AsyncSession,
        user_id: int,
        grocery_list_id: int,
        item_count: int,
    ) -> Notification:
        """
        Send notification when grocery list is generated.

        Args:
            db: Database session
            user_id: User ID
            grocery_list_id: Grocery list ID
            item_count: Number of items in the list

        Returns:
            Created notification
        """
        notification = await self.create_notification(
            db=db,
            user_id=user_id,
            notification_type="grocery_list_ready",
            title="Grocery List Ready!",
            message=f"Your grocery list with {item_count} items is ready.",
            data={
                "grocery_list_id": grocery_list_id,
                "item_count": item_count,
            },
            priority="low",
        )

        return notification

    async def _send_push_notification(
        self,
        notification: Notification,
    ) -> None:
        """
        Send push notification to user's device.

        PLACEHOLDER: Mock implementation for hackathon.
        In production, integrate with:
        - Firebase Cloud Messaging (FCM) for mobile
        - WebSocket for real-time browser notifications
        - Email service for important notifications

        Args:
            notification: Notification to send
        """
        logger.info(
            f"[MOCK] Sending push notification to user {notification.user_id}: "
            f"{notification.title}"
        )

        # PLACEHOLDER: In production, implement:
        # if notification.priority in ["high", "urgent"]:
        #     await send_fcm_notification(notification)
        #     await send_email_notification(notification)
        # await broadcast_websocket_notification(notification)


# Singleton instance
notification_service = NotificationService()
