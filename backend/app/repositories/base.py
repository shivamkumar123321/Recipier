"""
Base repository with common CRUD operations.

Provides generic database operations that can be inherited by
specific repository classes.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository providing common CRUD operations.

    Type Parameters:
        ModelType: SQLAlchemy model class

    Attributes:
        model: SQLAlchemy model class for this repository
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize repository with model class.

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    async def get(
        self,
        db: AsyncSession,
        id: int
    ) -> Optional[ModelType]:
        """
        Get a single record by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Model instance if found, None otherwise
        """
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.

        Args:
            db: Database session
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        result = await db.execute(
            select(self.model)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(
        self,
        db: AsyncSession,
        obj_in: Dict[str, Any]
    ) -> ModelType:
        """
        Create a new record.

        Args:
            db: Database session
            obj_in: Dictionary of field values

        Returns:
            Created model instance
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: Dict[str, Any]
    ) -> ModelType:
        """
        Update an existing record.

        Args:
            db: Database session
            db_obj: Existing model instance
            obj_in: Dictionary of fields to update

        Returns:
            Updated model instance
        """
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db: AsyncSession,
        id: int
    ) -> bool:
        """
        Delete a record (hard delete).

        Args:
            db: Database session
            id: Record ID to delete

        Returns:
            True if deleted, False if not found
        """
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        db_obj = result.scalar_one_or_none()

        if db_obj:
            await db.delete(db_obj)
            await db.flush()
            return True

        return False

    async def soft_delete(
        self,
        db: AsyncSession,
        id: int
    ) -> Optional[ModelType]:
        """
        Soft delete a record (set deleted_at timestamp).

        Args:
            db: Database session
            id: Record ID to soft delete

        Returns:
            Soft deleted model instance if found, None otherwise
        """
        db_obj = await self.get(db, id)

        if db_obj and hasattr(db_obj, 'soft_delete'):
            db_obj.soft_delete()
            await db.flush()
            await db.refresh(db_obj)
            return db_obj

        return None

    async def count(
        self,
        db: AsyncSession
    ) -> int:
        """
        Count total records.

        Args:
            db: Database session

        Returns:
            Total number of records
        """
        from sqlalchemy import func

        result = await db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0
