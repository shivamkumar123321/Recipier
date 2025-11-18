"""
User repository for user-related database operations.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for User model operations.

    Provides user-specific database queries beyond basic CRUD.
    """

    def __init__(self):
        super().__init__(User)

    async def get_by_email(
        self,
        db: AsyncSession,
        email: str
    ) -> Optional[User]:
        """
        Get user by email address.

        Args:
            db: Database session
            email: User email address

        Returns:
            User if found, None otherwise
        """
        result = await db.execute(
            select(User).where(
                User.email == email.lower(),
                User.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def email_exists(
        self,
        db: AsyncSession,
        email: str
    ) -> bool:
        """
        Check if email already exists.

        Args:
            db: Database session
            email: Email address to check

        Returns:
            True if email exists, False otherwise
        """
        user = await self.get_by_email(db, email)
        return user is not None

    async def get_active_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> list[User]:
        """
        Get all active users.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of active users
        """
        result = await db.execute(
            select(User)
            .where(
                User.is_active == True,
                User.deleted_at.is_(None)
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
