"""
Background scheduler for periodic tasks.

Uses APScheduler to run background tasks like:
- Checking for expiring items
- Sending notifications
- Cleaning up old data
"""

from datetime import date, timedelta
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.logging import get_logger
from app.repositories.inventory_repository import inventory_repository
from app.repositories.notification_repository import notification_repository
from app.repositories.user_repository import user_repository
from app.services.notification_service import notification_service

logger = get_logger(__name__)

# Create scheduler instance
scheduler = AsyncIOScheduler()


async def get_db_session() -> AsyncSession:
    """
    Create a database session for background tasks.

    Returns:
        AsyncSession for database operations
    """
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

    await engine.dispose()


async def check_expiring_items_task():
    """
    Background task to check for expiring inventory items.

    Runs daily at 9 AM.
    Sends notifications to users about items expiring within 3 days.
    """
    logger.info("Starting expiring items check task")

    async for db in get_db_session():
        try:
            # Get all active users
            users = await user_repository.get_multi(db, skip=0, limit=10000)
            logger.info(f"Checking expiring items for {len(users)} users")

            users_notified = 0

            for user in users:
                # Get expiring items for this user (within 3 days)
                expiring_items, _ = await inventory_repository.get_expiring_soon(
                    db=db,
                    user_id=user.id,
                    days=3,
                    skip=0,
                    limit=100,
                )

                if expiring_items:
                    # Format items for notification
                    items_data = [
                        {
                            "id": item.id,
                            "name": item.name,
                            "quantity": float(item.quantity),
                            "unit": item.unit,
                            "expiration_date": item.expiration_date.isoformat(),
                        }
                        for item in expiring_items
                    ]

                    # Send notification
                    await notification_service.send_expiring_items_notification(
                        db=db,
                        user_id=user.id,
                        expiring_items=items_data,
                    )

                    users_notified += 1
                    logger.info(
                        f"Sent expiring items notification to user {user.id} "
                        f"({len(expiring_items)} items)"
                    )

            await db.commit()

            logger.info(
                f"Expiring items check completed. "
                f"Notified {users_notified} users."
            )

        except Exception as e:
            logger.error(f"Error in expiring items check task: {e}", exc_info=True)
            await db.rollback()


async def cleanup_old_data_task():
    """
    Background task to clean up old data.

    Runs weekly (every Sunday at 2 AM).
    Cleans up:
    - Old notifications (older than 30 days)
    - Soft-deleted items (older than 90 days)
    """
    logger.info("Starting data cleanup task")

    async for db in get_db_session():
        try:
            # Clean up old notifications (30 days)
            notifications_deleted = await notification_repository.delete_old_notifications(
                db=db,
                days=30,
            )

            logger.info(f"Deleted {notifications_deleted} old notifications")

            # TODO: Add cleanup for soft-deleted items
            # TODO: Add cleanup for completed meal plans
            # TODO: Add cleanup for old activity logs

            await db.commit()

            logger.info(
                f"Data cleanup completed. "
                f"Deleted {notifications_deleted} notifications."
            )

        except Exception as e:
            logger.error(f"Error in data cleanup task: {e}", exc_info=True)
            await db.rollback()


async def test_scheduler_task():
    """
    Test task to verify scheduler is working.

    Runs every minute during development.
    Can be disabled in production.
    """
    logger.info("Scheduler test task executed successfully")


def start_scheduler():
    """
    Start the background scheduler with all scheduled tasks.

    Scheduled tasks:
    - check_expiring_items_task: Daily at 9 AM
    - cleanup_old_data_task: Weekly on Sunday at 2 AM
    - test_scheduler_task: Every minute (development only)
    """
    logger.info("Starting background scheduler")

    # Add scheduled tasks

    # Daily expiring items check at 9 AM
    scheduler.add_job(
        check_expiring_items_task,
        trigger=CronTrigger(hour=9, minute=0),
        id="check_expiring_items",
        name="Check for expiring inventory items",
        replace_existing=True,
    )
    logger.info("Scheduled task: Check expiring items (daily at 9 AM)")

    # Weekly data cleanup on Sunday at 2 AM
    scheduler.add_job(
        cleanup_old_data_task,
        trigger=CronTrigger(day_of_week="sun", hour=2, minute=0),
        id="cleanup_old_data",
        name="Clean up old data",
        replace_existing=True,
    )
    logger.info("Scheduled task: Data cleanup (Sunday at 2 AM)")

    # Test task (every minute - development only)
    if settings.ENVIRONMENT == "development":
        scheduler.add_job(
            test_scheduler_task,
            trigger=CronTrigger(minute="*"),
            id="test_scheduler",
            name="Scheduler test task",
            replace_existing=True,
        )
        logger.info("Scheduled task: Test task (every minute - development only)")

    # Start scheduler
    scheduler.start()
    logger.info("Background scheduler started successfully")


def stop_scheduler():
    """
    Stop the background scheduler.

    Should be called on application shutdown.
    """
    logger.info("Stopping background scheduler")
    scheduler.shutdown(wait=True)
    logger.info("Background scheduler stopped")


def get_scheduler_status() -> dict:
    """
    Get current scheduler status and job information.

    Returns:
        Dictionary with scheduler status and job list
    """
    jobs = []

    for job in scheduler.get_jobs():
        jobs.append(
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            }
        )

    return {
        "running": scheduler.running,
        "jobs": jobs,
        "job_count": len(jobs),
    }
