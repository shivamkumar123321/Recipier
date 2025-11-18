"""
Inventory repository for database operations.

Provides data access layer for inventory items.
"""

from datetime import date, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.models.inventory import FoodCategory, InventoryItem
from app.repositories.base import BaseRepository

logger = get_logger(__name__)


class InventoryRepository(BaseRepository[InventoryItem]):
    """Repository for inventory item operations."""

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        storage_location: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[InventoryItem], int]:
        """
        Get inventory items for a user with filtering, sorting, and pagination.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            category_id: Filter by category ID
            storage_location: Filter by storage location
            search: Search by item name
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)

        Returns:
            Tuple of (items list, total count)
        """
        # Build base query
        query = (
            select(InventoryItem)
            .where(
                InventoryItem.user_id == user_id,
                InventoryItem.deleted_at.is_(None),
            )
            .options(selectinload(InventoryItem.category))
        )

        # Apply filters
        if category_id is not None:
            query = query.where(InventoryItem.category_id == category_id)

        if storage_location:
            query = query.where(InventoryItem.storage_location == storage_location)

        if search:
            query = query.where(
                InventoryItem.name.ilike(f"%{search}%")
            )

        # Get total count before pagination
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply sorting
        sort_column = getattr(InventoryItem, sort_by, InventoryItem.created_at)
        if sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        result = await db.execute(query)
        items = result.scalars().all()

        return list(items), total

    async def get_expiring_soon(
        self,
        db: AsyncSession,
        user_id: int,
        days: int = 7,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[InventoryItem], int]:
        """
        Get items expiring within specified days.

        Args:
            db: Database session
            user_id: User ID
            days: Number of days to check for expiration
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (items list, total count)
        """
        expiration_threshold = date.today() + timedelta(days=days)

        query = (
            select(InventoryItem)
            .where(
                InventoryItem.user_id == user_id,
                InventoryItem.deleted_at.is_(None),
                InventoryItem.expiration_date.is_not(None),
                InventoryItem.expiration_date <= expiration_threshold,
                InventoryItem.expiration_date >= date.today(),
            )
            .options(selectinload(InventoryItem.category))
            .order_by(InventoryItem.expiration_date.asc())
        )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        items = result.scalars().all()

        return list(items), total

    async def get_by_expiration_range(
        self,
        db: AsyncSession,
        user_id: int,
        expiration_from: Optional[date] = None,
        expiration_to: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[InventoryItem], int]:
        """
        Get items within expiration date range.

        Args:
            db: Database session
            user_id: User ID
            expiration_from: Start date (inclusive)
            expiration_to: End date (inclusive)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (items list, total count)
        """
        conditions = [
            InventoryItem.user_id == user_id,
            InventoryItem.deleted_at.is_(None),
            InventoryItem.expiration_date.is_not(None),
        ]

        if expiration_from:
            conditions.append(InventoryItem.expiration_date >= expiration_from)

        if expiration_to:
            conditions.append(InventoryItem.expiration_date <= expiration_to)

        query = (
            select(InventoryItem)
            .where(and_(*conditions))
            .options(selectinload(InventoryItem.category))
            .order_by(InventoryItem.expiration_date.asc())
        )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        items = result.scalars().all()

        return list(items), total

    async def get_by_categories(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> List[Tuple[Optional[int], Optional[str], List[InventoryItem]]]:
        """
        Get inventory items grouped by category.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of tuples (category_id, category_name, items)
        """
        query = (
            select(InventoryItem)
            .where(
                InventoryItem.user_id == user_id,
                InventoryItem.deleted_at.is_(None),
            )
            .options(selectinload(InventoryItem.category))
            .order_by(InventoryItem.category_id, InventoryItem.name)
        )

        result = await db.execute(query)
        items = result.scalars().all()

        # Group by category
        grouped = {}
        for item in items:
            category_id = item.category_id
            category_name = item.category.name if item.category else None

            if category_id not in grouped:
                grouped[category_id] = (category_id, category_name, [])

            grouped[category_id][2].append(item)

        return list(grouped.values())

    async def get_by_id_and_user(
        self,
        db: AsyncSession,
        item_id: int,
        user_id: int,
    ) -> Optional[InventoryItem]:
        """
        Get inventory item by ID and verify user ownership.

        Args:
            db: Database session
            item_id: Item ID
            user_id: User ID

        Returns:
            Inventory item if found and owned by user, None otherwise
        """
        result = await db.execute(
            select(InventoryItem)
            .where(
                InventoryItem.id == item_id,
                InventoryItem.user_id == user_id,
                InventoryItem.deleted_at.is_(None),
            )
            .options(selectinload(InventoryItem.category))
        )

        return result.scalar_one_or_none()

    async def bulk_create(
        self,
        db: AsyncSession,
        items_data: List[dict],
        user_id: int,
    ) -> List[InventoryItem]:
        """
        Create multiple inventory items at once.

        Args:
            db: Database session
            items_data: List of item data dictionaries
            user_id: User ID

        Returns:
            List of created inventory items
        """
        items = []
        for data in items_data:
            data["user_id"] = user_id
            item = InventoryItem(**data)
            db.add(item)
            items.append(item)

        await db.flush()

        # Reload with relationships
        for item in items:
            await db.refresh(item, ["category"])

        return items


class FoodCategoryRepository(BaseRepository[FoodCategory]):
    """Repository for food category operations."""

    async def get_by_name(
        self,
        db: AsyncSession,
        name: str,
    ) -> Optional[FoodCategory]:
        """
        Get category by name.

        Args:
            db: Database session
            name: Category name

        Returns:
            Food category if found, None otherwise
        """
        result = await db.execute(
            select(FoodCategory).where(
                FoodCategory.name.ilike(name)
            )
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
    ) -> List[FoodCategory]:
        """
        Get all food categories.

        Args:
            db: Database session

        Returns:
            List of all food categories
        """
        result = await db.execute(
            select(FoodCategory).order_by(FoodCategory.name)
        )

        return list(result.scalars().all())


# Singleton instances
inventory_repository = InventoryRepository(InventoryItem)
food_category_repository = FoodCategoryRepository(FoodCategory)
