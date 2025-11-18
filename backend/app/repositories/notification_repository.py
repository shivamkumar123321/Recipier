"""
Notification repository for database operations.

Provides data access layer for user notifications.
"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.notification import Notification
from app.repositories.base import BaseRepository

logger = get_logger(__name__)


class NotificationRepository(BaseRepository[Notification]):
    """Repository for notification operations."""

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        unread_only: bool = False,
    ) -> Tuple[List[Notification], int, int]:
        """
        Get notifications for a user with pagination.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            unread_only: Filter to only unread notifications

        Returns:
            Tuple of (notifications list, total count, unread count)
        """
        # Build base query
        conditions = [Notification.user_id == user_id]

        if unread_only:
            conditions.append(Notification.is_read == False)

        query = (
            select(Notification)
            .where(and_(*conditions))
            .order_by(Notification.created_at.desc())
        )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Get unread count (always)
        unread_query = select(func.count()).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        unread_result = await db.execute(unread_query)
        unread_count = unread_result.scalar() or 0

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        result = await db.execute(query)
        notifications = result.scalars().all()

        return list(notifications), total, unread_count

    async def get_by_id_and_user(
        self,
        db: AsyncSession,
        notification_id: int,
        user_id: int,
    ) -> Optional[Notification]:
        """
        Get notification by ID and verify user ownership.

        Args:
            db: Database session
            notification_id: Notification ID
            user_id: User ID

        Returns:
            Notification if found and owned by user, None otherwise
        """
        result = await db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def mark_as_read(
        self,
        db: AsyncSession,
        notification_id: int,
        is_read: bool = True,
    ) -> Optional[Notification]:
        """
        Mark notification as read or unread.

        Args:
            db: Database session
            notification_id: Notification ID
            is_read: Whether to mark as read (True) or unread (False)

        Returns:
            Updated notification if found, None otherwise
        """
        notification = await self.get(db, notification_id)

        if notification:
            notification.is_read = is_read
            if is_read:
                notification.read_at = datetime.utcnow().isoformat()
            else:
                notification.read_at = None

            await db.flush()
            await db.refresh(notification)

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
            Number of notifications updated
        """
        # Get all unread notifications
        result = await db.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
        )
        notifications = result.scalars().all()

        # Mark each as read
        count = 0
        read_at = datetime.utcnow().isoformat()

        for notification in notifications:
            notification.is_read = True
            notification.read_at = read_at
            count += 1

        if count > 0:
            await db.flush()

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
        # Get notifications
        result = await db.execute(
            select(Notification).where(
                Notification.id.in_(notification_ids),
                Notification.user_id == user_id,
            )
        )
        notifications = result.scalars().all()

        # Update each notification
        count = 0
        read_at = datetime.utcnow().isoformat() if is_read else None

        for notification in notifications:
            notification.is_read = is_read
            notification.read_at = read_at
            count += 1

        if count > 0:
            await db.flush()

        return count

    async def delete_old_notifications(
        self,
        db: AsyncSession,
        days: int = 30,
    ) -> int:
        """
        Delete notifications older than specified days.

        Args:
            db: Database session
            days: Number of days to keep notifications

        Returns:
            Number of notifications deleted
        """
        cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)

        # Get old notifications
        result = await db.execute(
            select(Notification).where(
                Notification.created_at < cutoff_date.isoformat()
            )
        )
        notifications = result.scalars().all()

        # Delete each notification
        count = 0
        for notification in notifications:
            await db.delete(notification)
            count += 1

        if count > 0:
            await db.flush()

        logger.info(f"Deleted {count} notifications older than {days} days")
        return count


# Singleton instance
notification_repository = NotificationRepository(Notification)
