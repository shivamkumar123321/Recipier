"""
Meal plan repository for database operations.

Provides data access layer for meal plans and meal plan items.
"""

from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.models.meal_plan import MealPlan, MealPlanItem
from app.repositories.base import BaseRepository

logger = get_logger(__name__)


class MealPlanRepository(BaseRepository[MealPlan]):
    """Repository for meal plan operations."""

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> Tuple[List[MealPlan], int]:
        """
        Get meal plans for a user with filtering and pagination.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status (active/completed/archived)

        Returns:
            Tuple of (meal plans list, total count)
        """
        conditions = [MealPlan.user_id == user_id]

        if status:
            conditions.append(MealPlan.status == status)

        query = select(MealPlan).where(and_(*conditions))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply sorting and pagination
        query = (
            query.order_by(MealPlan.start_date.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(query)
        meal_plans = result.scalars().all()

        return list(meal_plans), total

    async def get_by_id_and_user(
        self,
        db: AsyncSession,
        meal_plan_id: int,
        user_id: int,
    ) -> Optional[MealPlan]:
        """
        Get meal plan by ID and verify user ownership.

        Args:
            db: Database session
            meal_plan_id: Meal plan ID
            user_id: User ID

        Returns:
            Meal plan if found and owned by user, None otherwise
        """
        result = await db.execute(
            select(MealPlan)
            .where(
                MealPlan.id == meal_plan_id,
                MealPlan.user_id == user_id,
            )
            .options(selectinload(MealPlan.meal_plan_items))
        )

        return result.scalar_one_or_none()

    async def get_by_id_with_items(
        self,
        db: AsyncSession,
        meal_plan_id: int,
    ) -> Optional[MealPlan]:
        """
        Get meal plan by ID with all items.

        Args:
            db: Database session
            meal_plan_id: Meal plan ID

        Returns:
            Meal plan with items if found, None otherwise
        """
        result = await db.execute(
            select(MealPlan)
            .where(MealPlan.id == meal_plan_id)
            .options(selectinload(MealPlan.meal_plan_items))
        )

        return result.scalar_one_or_none()

    async def get_active_for_date(
        self,
        db: AsyncSession,
        user_id: int,
        target_date: date,
    ) -> Optional[MealPlan]:
        """
        Get active meal plan for a specific date.

        Args:
            db: Database session
            user_id: User ID
            target_date: Target date

        Returns:
            Active meal plan if found, None otherwise
        """
        result = await db.execute(
            select(MealPlan).where(
                MealPlan.user_id == user_id,
                MealPlan.status == "active",
                MealPlan.start_date <= target_date,
                MealPlan.end_date >= target_date,
            )
        )

        return result.scalar_one_or_none()


class MealPlanItemRepository(BaseRepository[MealPlanItem]):
    """Repository for meal plan item operations."""

    async def get_by_meal_plan(
        self,
        db: AsyncSession,
        meal_plan_id: int,
    ) -> List[MealPlanItem]:
        """
        Get all items for a meal plan.

        Args:
            db: Database session
            meal_plan_id: Meal plan ID

        Returns:
            List of meal plan items
        """
        result = await db.execute(
            select(MealPlanItem)
            .where(MealPlanItem.meal_plan_id == meal_plan_id)
            .options(selectinload(MealPlanItem.recipe))
            .order_by(
                MealPlanItem.scheduled_date,
                MealPlanItem.meal_type,
            )
        )

        return list(result.scalars().all())

    async def get_by_date_range(
        self,
        db: AsyncSession,
        meal_plan_id: int,
        start_date: date,
        end_date: date,
    ) -> List[MealPlanItem]:
        """
        Get meal plan items within a date range.

        Args:
            db: Database session
            meal_plan_id: Meal plan ID
            start_date: Start date
            end_date: End date

        Returns:
            List of meal plan items
        """
        result = await db.execute(
            select(MealPlanItem)
            .where(
                MealPlanItem.meal_plan_id == meal_plan_id,
                MealPlanItem.scheduled_date >= start_date,
                MealPlanItem.scheduled_date <= end_date,
            )
            .options(selectinload(MealPlanItem.recipe))
            .order_by(
                MealPlanItem.scheduled_date,
                MealPlanItem.meal_type,
            )
        )

        return list(result.scalars().all())

    async def bulk_create(
        self,
        db: AsyncSession,
        meal_plan_id: int,
        items_data: List[dict],
    ) -> List[MealPlanItem]:
        """
        Create multiple meal plan items at once.

        Args:
            db: Database session
            meal_plan_id: Meal plan ID
            items_data: List of item data dictionaries

        Returns:
            List of created meal plan items
        """
        items = []
        for data in items_data:
            data["meal_plan_id"] = meal_plan_id
            item = MealPlanItem(**data)
            db.add(item)
            items.append(item)

        await db.flush()

        # Reload with relationships
        for item in items:
            await db.refresh(item, ["recipe"])

        return items

    async def mark_as_completed(
        self,
        db: AsyncSession,
        item_id: int,
    ) -> Optional[MealPlanItem]:
        """
        Mark a meal plan item as completed.

        Args:
            db: Database session
            item_id: Meal plan item ID

        Returns:
            Updated meal plan item if found, None otherwise
        """
        item = await self.get(db, item_id)
        if item:
            item.is_completed = True
            await db.flush()
            await db.refresh(item)

        return item


# Singleton instances
meal_plan_repository = MealPlanRepository(MealPlan)
meal_plan_item_repository = MealPlanItemRepository(MealPlanItem)
