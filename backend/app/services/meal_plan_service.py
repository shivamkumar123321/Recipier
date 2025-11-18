"""
Meal plan service for business logic.

Handles meal plan creation, AI generation, and meal cooking workflow.
"""

from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.meal_plan import MealPlan, MealPlanItem
from app.repositories.inventory_repository import inventory_repository
from app.repositories.meal_plan_repository import (
    meal_plan_item_repository,
    meal_plan_repository,
)
from app.repositories.recipe_repository import (
    recipe_ingredient_repository,
    recipe_repository,
)
from app.schemas.meal_plan import (
    MealPlanCreate,
    MealPlanGenerateRequest,
)

logger = get_logger(__name__)


class MealPlanService:
    """Service for meal plan operations."""

    async def get_user_meal_plans(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> Tuple[List[MealPlan], int]:
        """
        Get user's meal plans with filtering and pagination.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status (active/completed/archived)

        Returns:
            Tuple of (meal plans list, total count)
        """
        logger.info(f"Fetching meal plans for user {user_id}, status={status}")

        meal_plans, total = await meal_plan_repository.get_by_user(
            db, user_id, skip, limit, status
        )

        logger.info(f"Found {total} meal plans")
        return meal_plans, total

    async def get_meal_plan_by_id(
        self,
        db: AsyncSession,
        meal_plan_id: int,
        user_id: int,
    ) -> MealPlan:
        """
        Get meal plan by ID with verification of user ownership.

        Args:
            db: Database session
            meal_plan_id: Meal plan ID
            user_id: User ID

        Returns:
            Meal plan with items

        Raises:
            HTTPException: If meal plan not found or not owned by user
        """
        logger.info(f"Fetching meal plan {meal_plan_id} for user {user_id}")

        meal_plan = await meal_plan_repository.get_by_id_and_user(
            db, meal_plan_id, user_id
        )

        if not meal_plan:
            logger.warning(f"Meal plan {meal_plan_id} not found or access denied")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal plan not found",
            )

        return meal_plan

    async def create_meal_plan(
        self,
        db: AsyncSession,
        meal_plan_data: MealPlanCreate,
        user_id: int,
    ) -> MealPlan:
        """
        Create a new meal plan.

        Args:
            db: Database session
            meal_plan_data: Meal plan creation data
            user_id: User ID

        Returns:
            Created meal plan
        """
        logger.info(f"Creating meal plan: {meal_plan_data.name} for user {user_id}")

        meal_plan_dict = meal_plan_data.model_dump()
        meal_plan_dict["user_id"] = user_id

        meal_plan = await meal_plan_repository.create(db, meal_plan_dict)
        await db.commit()
        await db.refresh(meal_plan)

        logger.info(f"Meal plan created successfully: {meal_plan.id}")
        return meal_plan

    async def generate_ai_meal_plan(
        self,
        db: AsyncSession,
        request: MealPlanGenerateRequest,
        user_id: int,
    ) -> MealPlan:
        """
        Generate AI-powered meal plan based on user preferences.

        This is a PLACEHOLDER for AI integration. In production, this would:
        1. Use GPT-4 to generate personalized meal suggestions
        2. Consider user's dietary preferences and restrictions
        3. Balance macros and calories across meals
        4. Match recipes from database or create new ones
        5. Account for ingredient availability in user's inventory

        Args:
            db: Database session
            request: Generation request with preferences
            user_id: User ID

        Returns:
            Generated meal plan with scheduled meals

        Raises:
            HTTPException: If generation fails
        """
        logger.info(f"Generating AI meal plan for user {user_id}")
        logger.info(
            f"Parameters: {request.start_date} to {request.end_date}, "
            f"calories={request.target_calories}, preferences={request.dietary_preferences}"
        )

        # PLACEHOLDER: In production, call OpenAI API here
        # For now, create a basic meal plan structure

        # Create meal plan
        meal_plan_dict = {
            "user_id": user_id,
            "name": request.name,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "target_calories": request.target_calories,
            "macro_targets": request.macro_targets,
            "status": "active",
        }

        meal_plan = await meal_plan_repository.create(db, meal_plan_dict)

        # PLACEHOLDER: Generate meal plan items
        # In production, this would be AI-generated based on:
        # - User preferences (dietary_preferences, excluded_ingredients)
        # - Available recipes in database
        # - Nutritional targets (target_calories, macro_targets)
        # - Meal types requested (meal_types)

        items_data = []
        current_date = request.start_date
        item_index = 0

        while current_date <= request.end_date:
            for meal_type in request.meal_types:
                items_data.append(
                    {
                        "scheduled_date": current_date,
                        "meal_type": meal_type,
                        "servings": 1,
                        "notes": f"AI-generated {meal_type} - PLACEHOLDER",
                        "is_completed": False,
                        "recipe_id": None,  # Would be populated by AI
                    }
                )
                item_index += 1

            current_date += timedelta(days=1)

        # Create meal plan items
        if items_data:
            await meal_plan_item_repository.bulk_create(
                db, meal_plan.id, items_data
            )

        await db.commit()

        # Reload with items
        meal_plan_full = await meal_plan_repository.get_by_id_with_items(
            db, meal_plan.id
        )

        logger.info(
            f"AI meal plan generated with {len(items_data)} meals (PLACEHOLDER MODE)"
        )
        logger.warning(
            "AI meal plan generation is currently using placeholder logic. "
            "Integrate OpenAI API for production."
        )

        return meal_plan_full

    async def cook_meal(
        self,
        db: AsyncSession,
        meal_plan_id: int,
        meal_plan_item_id: int,
        user_id: int,
    ) -> Dict:
        """
        Mark a meal as cooked and update inventory.

        This workflow:
        1. Marks the meal plan item as completed
        2. Deducts ingredients from user's inventory
        3. Returns summary of changes

        Args:
            db: Database session
            meal_plan_id: Meal plan ID
            meal_plan_item_id: Meal plan item ID to mark as cooked
            user_id: User ID

        Returns:
            Dictionary with meal item, inventory update status, and summary

        Raises:
            HTTPException: If meal plan or item not found, or access denied
        """
        logger.info(
            f"Cooking meal: plan={meal_plan_id}, item={meal_plan_item_id}, user={user_id}"
        )

        # Verify meal plan ownership
        meal_plan = await meal_plan_repository.get_by_id_and_user(
            db, meal_plan_id, user_id
        )
        if not meal_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal plan not found",
            )

        # Get meal plan item
        meal_item = await meal_plan_item_repository.get(db, meal_plan_item_id)
        if not meal_item or meal_item.meal_plan_id != meal_plan_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal plan item not found",
            )

        if meal_item.is_completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meal already marked as cooked",
            )

        # Mark as completed
        meal_item = await meal_plan_item_repository.mark_as_completed(
            db, meal_plan_item_id
        )

        items_deducted = 0
        inventory_updated = False

        # Deduct ingredients from inventory if recipe is linked
        if meal_item.recipe_id:
            logger.info(f"Deducting ingredients for recipe {meal_item.recipe_id}")

            # Get recipe ingredients
            ingredients = await recipe_ingredient_repository.get_by_recipe(
                db, meal_item.recipe_id
            )

            # Deduct from inventory
            for ingredient in ingredients:
                # Find matching inventory item
                inventory_items, _ = await inventory_repository.get_by_user(
                    db=db,
                    user_id=user_id,
                    search=ingredient.ingredient_name,
                    limit=1,
                )

                if inventory_items:
                    inventory_item = inventory_items[0]

                    # Calculate quantity to deduct (scaled by servings)
                    quantity_needed = ingredient.quantity * meal_item.servings

                    # Deduct quantity (don't go below 0)
                    new_quantity = max(0, inventory_item.quantity - quantity_needed)

                    await inventory_repository.update(
                        db,
                        inventory_item,
                        {"quantity": new_quantity},
                    )

                    items_deducted += 1
                    inventory_updated = True

                    logger.debug(
                        f"Deducted {quantity_needed} {ingredient.unit} "
                        f"of {ingredient.ingredient_name}"
                    )

        await db.commit()
        await db.refresh(meal_item)

        logger.info(
            f"Meal cooked successfully. Inventory items updated: {items_deducted}"
        )

        return {
            "meal_plan_item": meal_item,
            "inventory_updated": inventory_updated,
            "items_deducted": items_deducted,
            "message": (
                f"Meal marked as cooked. "
                f"{items_deducted} inventory items updated."
                if inventory_updated
                else "Meal marked as cooked. No inventory updates."
            ),
        }


# Singleton instance
meal_plan_service = MealPlanService()
