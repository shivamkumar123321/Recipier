"""
Tests for notification API endpoints.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.notification_repository import notification_repository


@pytest.mark.asyncio
async def test_get_notifications_empty(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test getting notifications when none exist."""
    response = await client.get(
        "/api/v1/notifications/",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["unread_count"] == 0
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_get_notifications(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test getting user's notifications."""
    # Create test notifications
    for i in range(3):
        await notification_repository.create(
            db,
            {
                "user_id": verified_user.id,
                "notification_type": "test",
                "title": f"Test Notification {i}",
                "message": f"This is test notification {i}",
                "priority": "medium",
                "is_read": i == 0,  # First one is read
            },
        )
    await db.commit()

    # Get all notifications
    response = await client.get(
        "/api/v1/notifications/",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["unread_count"] == 2
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_get_unread_notifications_only(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test getting only unread notifications."""
    # Create mix of read and unread notifications
    for i in range(5):
        await notification_repository.create(
            db,
            {
                "user_id": verified_user.id,
                "notification_type": "test",
                "title": f"Notification {i}",
                "message": f"Message {i}",
                "priority": "medium",
                "is_read": i < 2,  # First 2 are read
            },
        )
    await db.commit()

    # Get only unread
    response = await client.get(
        "/api/v1/notifications/?unread_only=true",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3  # Only unread
    assert data["unread_count"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_mark_notification_as_read(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test marking a notification as read."""
    # Create notification
    notification = await notification_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "notification_type": "test",
            "title": "Test Notification",
            "message": "Test message",
            "priority": "medium",
            "is_read": False,
        },
    )
    await db.commit()

    # Mark as read
    response = await client.patch(
        f"/api/v1/notifications/{notification.id}/read",
        headers=verified_auth_headers,
        json={"is_read": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is True
    assert data["read_at"] is not None


@pytest.mark.asyncio
async def test_mark_notification_as_unread(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test marking a notification as unread."""
    # Create read notification
    notification = await notification_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "notification_type": "test",
            "title": "Test Notification",
            "message": "Test message",
            "priority": "medium",
            "is_read": True,
        },
    )
    await db.commit()

    # Mark as unread
    response = await client.patch(
        f"/api/v1/notifications/{notification.id}/read",
        headers=verified_auth_headers,
        json={"is_read": False},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is False
    assert data["read_at"] is None


@pytest.mark.asyncio
async def test_mark_notification_not_found(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test marking a non-existent notification."""
    response = await client.patch(
        "/api/v1/notifications/999999/read",
        headers=verified_auth_headers,
        json={"is_read": True},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_mark_notification_unauthorized(
    client: AsyncClient,
    test_user: User,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test marking another user's notification."""
    # Create notification for test_user
    notification = await notification_repository.create(
        db,
        {
            "user_id": test_user.id,  # Different user
            "notification_type": "test",
            "title": "Test Notification",
            "message": "Test message",
            "priority": "medium",
            "is_read": False,
        },
    )
    await db.commit()

    # Try to mark as read with verified_user's token
    response = await client.patch(
        f"/api/v1/notifications/{notification.id}/read",
        headers=verified_auth_headers,
        json={"is_read": True},
    )

    assert response.status_code == 404  # Not found (access denied)


@pytest.mark.asyncio
async def test_mark_all_as_read(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test marking all notifications as read."""
    # Create unread notifications
    for i in range(5):
        await notification_repository.create(
            db,
            {
                "user_id": verified_user.id,
                "notification_type": "test",
                "title": f"Notification {i}",
                "message": f"Message {i}",
                "priority": "medium",
                "is_read": False,
            },
        )
    await db.commit()

    # Mark all as read
    response = await client.post(
        "/api/v1/notifications/mark-all-read",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 5

    # Verify all are read
    response = await client.get(
        "/api/v1/notifications/",
        headers=verified_auth_headers,
    )

    data = response.json()
    assert data["unread_count"] == 0


@pytest.mark.asyncio
async def test_bulk_mark_as_read(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test bulk marking notifications as read."""
    # Create notifications
    notification_ids = []
    for i in range(5):
        notification = await notification_repository.create(
            db,
            {
                "user_id": verified_user.id,
                "notification_type": "test",
                "title": f"Notification {i}",
                "message": f"Message {i}",
                "priority": "medium",
                "is_read": False,
            },
        )
        notification_ids.append(notification.id)
    await db.commit()

    # Mark first 3 as read
    response = await client.post(
        "/api/v1/notifications/bulk-mark-read",
        headers=verified_auth_headers,
        json={
            "notification_ids": notification_ids[:3],
            "is_read": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 3

    # Verify unread count
    response = await client.get(
        "/api/v1/notifications/",
        headers=verified_auth_headers,
    )

    data = response.json()
    assert data["unread_count"] == 2  # 5 - 3 = 2


@pytest.mark.asyncio
async def test_get_unread_count(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test getting unread notification count."""
    # Create mix of read and unread
    for i in range(10):
        await notification_repository.create(
            db,
            {
                "user_id": verified_user.id,
                "notification_type": "test",
                "title": f"Notification {i}",
                "message": f"Message {i}",
                "priority": "medium",
                "is_read": i < 4,  # First 4 are read
            },
        )
    await db.commit()

    # Get unread count
    response = await client.get(
        "/api/v1/notifications/unread-count",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["unread_count"] == 6  # 10 - 4 = 6


@pytest.mark.asyncio
async def test_notification_pagination(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test notification pagination."""
    # Create many notifications
    for i in range(10):
        await notification_repository.create(
            db,
            {
                "user_id": verified_user.id,
                "notification_type": "test",
                "title": f"Notification {i}",
                "message": f"Message {i}",
                "priority": "medium",
                "is_read": False,
            },
        )
    await db.commit()

    # Get first page
    response = await client.get(
        "/api/v1/notifications/?skip=0&limit=5",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 10
    assert len(data["items"]) == 5

    # Get second page
    response = await client.get(
        "/api/v1/notifications/?skip=5&limit=5",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 10
    assert len(data["items"]) == 5


@pytest.mark.asyncio
async def test_notification_priority_levels(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test notifications with different priority levels."""
    priorities = ["low", "medium", "high", "urgent"]

    for priority in priorities:
        await notification_repository.create(
            db,
            {
                "user_id": verified_user.id,
                "notification_type": "test",
                "title": f"{priority.title()} Priority",
                "message": f"This is a {priority} priority notification",
                "priority": priority,
                "is_read": False,
            },
        )
    await db.commit()

    # Get all notifications
    response = await client.get(
        "/api/v1/notifications/",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4

    # Verify all priorities are present
    notification_priorities = [n["priority"] for n in data["items"]]
    for priority in priorities:
        assert priority in notification_priorities
