"""
Grocery list repository for database operations.

Provides data access layer for grocery lists and grocery list items.
"""

from typing import List, Optional, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.models.grocery import GroceryList, GroceryListItem
from app.repositories.base import BaseRepository

logger = get_logger(__name__)


class GroceryListRepository(BaseRepository[GroceryList]):
    """Repository for grocery list operations."""

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> Tuple[List[GroceryList], int]:
        """
        Get grocery lists for a user with filtering and pagination.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status (active/completed/archived)

        Returns:
            Tuple of (grocery lists, total count)
        """
        conditions = [GroceryList.user_id == user_id]

        if status:
            conditions.append(GroceryList.status == status)

        query = (
            select(GroceryList)
            .where(and_(*conditions))
            .options(selectinload(GroceryList.items))
        )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply sorting and pagination
        query = query.order_by(GroceryList.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        grocery_lists = result.scalars().all()

        return list(grocery_lists), total

    async def get_by_id_and_user(
        self,
        db: AsyncSession,
        grocery_list_id: int,
        user_id: int,
    ) -> Optional[GroceryList]:
        """
        Get grocery list by ID and verify user ownership.

        Args:
            db: Database session
            grocery_list_id: Grocery list ID
            user_id: User ID

        Returns:
            Grocery list if found and owned by user, None otherwise
        """
        result = await db.execute(
            select(GroceryList)
            .where(
                GroceryList.id == grocery_list_id,
                GroceryList.user_id == user_id,
            )
            .options(selectinload(GroceryList.items))
        )

        return result.scalar_one_or_none()

    async def get_by_meal_plan(
        self,
        db: AsyncSession,
        meal_plan_id: int,
        user_id: int,
    ) -> Optional[GroceryList]:
        """
        Get grocery list by meal plan ID.

        Args:
            db: Database session
            meal_plan_id: Meal plan ID
            user_id: User ID

        Returns:
            Grocery list if found, None otherwise
        """
        result = await db.execute(
            select(GroceryList)
            .where(
                GroceryList.meal_plan_id == meal_plan_id,
                GroceryList.user_id == user_id,
            )
            .options(selectinload(GroceryList.items))
        )

        return result.scalar_one_or_none()


class GroceryListItemRepository(BaseRepository[GroceryListItem]):
    """Repository for grocery list item operations."""

    async def get_by_grocery_list(
        self,
        db: AsyncSession,
        grocery_list_id: int,
    ) -> List[GroceryListItem]:
        """
        Get all items for a grocery list.

        Args:
            db: Database session
            grocery_list_id: Grocery list ID

        Returns:
            List of grocery list items
        """
        result = await db.execute(
            select(GroceryListItem)
            .where(GroceryListItem.grocery_list_id == grocery_list_id)
            .options(selectinload(GroceryListItem.category))
            .order_by(GroceryListItem.order_index)
        )

        return list(result.scalars().all())

    async def bulk_create(
        self,
        db: AsyncSession,
        grocery_list_id: int,
        items_data: List[dict],
    ) -> List[GroceryListItem]:
        """
        Create multiple grocery list items at once.

        Args:
            db: Database session
            grocery_list_id: Grocery list ID
            items_data: List of item data dictionaries

        Returns:
            List of created grocery list items
        """
        items = []
        for data in items_data:
            data["grocery_list_id"] = grocery_list_id
            item = GroceryListItem(**data)
            db.add(item)
            items.append(item)

        await db.flush()

        # Reload with relationships
        for item in items:
            await db.refresh(item, ["category"])

        return items

    async def check_item(
        self,
        db: AsyncSession,
        item_id: int,
        is_checked: bool,
    ) -> Optional[GroceryListItem]:
        """
        Check or uncheck a grocery list item.

        Args:
            db: Database session
            item_id: Grocery list item ID
            is_checked: Whether the item is checked

        Returns:
            Updated grocery list item if found, None otherwise
        """
        item = await self.get(db, item_id)
        if item:
            item.is_checked = is_checked
            await db.flush()
            await db.refresh(item)

        return item


# Singleton instances
grocery_list_repository = GroceryListRepository(GroceryList)
grocery_list_item_repository = GroceryListItemRepository(GroceryListItem)
