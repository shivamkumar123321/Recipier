"""
Grocery list service for business logic.

Handles grocery list creation, generation from meal plans, and item management.
"""

from typing import Dict, List, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.grocery import GroceryList, GroceryListItem
from app.repositories.grocery_repository import (
    grocery_list_item_repository,
    grocery_list_repository,
)
from app.repositories.inventory_repository import inventory_repository
from app.repositories.meal_plan_repository import (
    meal_plan_item_repository,
    meal_plan_repository,
)
from app.repositories.recipe_repository import recipe_ingredient_repository
from app.schemas.grocery import GroceryListCreate, GroceryListGenerateRequest

logger = get_logger(__name__)


class GroceryListService:
    """Service for grocery list operations."""

    async def get_user_grocery_lists(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: str = None,
    ) -> Tuple[List[GroceryList], int]:
        """
        Get user's grocery lists with filtering and pagination.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status (active/completed/archived)

        Returns:
            Tuple of (grocery lists, total count)
        """
        logger.info(f"Fetching grocery lists for user {user_id}, status={status}")

        grocery_lists, total = await grocery_list_repository.get_by_user(
            db, user_id, skip, limit, status
        )

        logger.info(f"Found {total} grocery lists")
        return grocery_lists, total

    async def get_grocery_list_by_id(
        self,
        db: AsyncSession,
        grocery_list_id: int,
        user_id: int,
    ) -> GroceryList:
        """
        Get grocery list by ID with verification of user ownership.

        Args:
            db: Database session
            grocery_list_id: Grocery list ID
            user_id: User ID

        Returns:
            Grocery list with items

        Raises:
            HTTPException: If grocery list not found or not owned by user
        """
        logger.info(f"Fetching grocery list {grocery_list_id} for user {user_id}")

        grocery_list = await grocery_list_repository.get_by_id_and_user(
            db, grocery_list_id, user_id
        )

        if not grocery_list:
            logger.warning(
                f"Grocery list {grocery_list_id} not found or access denied"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grocery list not found",
            )

        return grocery_list

    async def create_grocery_list(
        self,
        db: AsyncSession,
        grocery_list_data: GroceryListCreate,
        user_id: int,
    ) -> GroceryList:
        """
        Create a new grocery list.

        Args:
            db: Database session
            grocery_list_data: Grocery list creation data
            user_id: User ID

        Returns:
            Created grocery list
        """
        logger.info(f"Creating grocery list: {grocery_list_data.name} for user {user_id}")

        grocery_list_dict = grocery_list_data.model_dump()
        grocery_list_dict["user_id"] = user_id

        grocery_list = await grocery_list_repository.create(db, grocery_list_dict)
        await db.commit()
        await db.refresh(grocery_list)

        logger.info(f"Grocery list created successfully: {grocery_list.id}")
        return grocery_list

    async def generate_from_meal_plan(
        self,
        db: AsyncSession,
        request: GroceryListGenerateRequest,
        user_id: int,
    ) -> Dict:
        """
        Generate grocery list from a meal plan.

        This workflow:
        1. Gets all meals from the meal plan
        2. Extracts ingredients from linked recipes
        3. Aggregates quantities for duplicate items
        4. Optionally excludes items already in inventory
        5. Creates grocery list with all items

        Args:
            db: Database session
            request: Generation request with meal plan ID and options
            user_id: User ID

        Returns:
            Dictionary with created grocery list and metadata

        Raises:
            HTTPException: If meal plan not found or access denied
        """
        logger.info(
            f"Generating grocery list from meal plan {request.meal_plan_id} "
            f"for user {user_id}"
        )

        # Verify meal plan ownership
        meal_plan = await meal_plan_repository.get_by_id_and_user(
            db, request.meal_plan_id, user_id
        )
        if not meal_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal plan not found",
            )

        # Check if grocery list already exists for this meal plan
        existing_list = await grocery_list_repository.get_by_meal_plan(
            db, request.meal_plan_id, user_id
        )
        if existing_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Grocery list already exists for this meal plan",
            )

        # Get all meal plan items
        meal_items = await meal_plan_item_repository.get_by_meal_plan(
            db, request.meal_plan_id
        )

        # Aggregate ingredients from all recipes
        ingredient_map = {}  # {(name, unit): quantity}

        for meal_item in meal_items:
            if meal_item.recipe_id and not meal_item.is_completed:
                # Get recipe ingredients
                ingredients = await recipe_ingredient_repository.get_by_recipe(
                    db, meal_item.recipe_id
                )

                for ingredient in ingredients:
                    key = (ingredient.ingredient_name.lower(), ingredient.unit)
                    quantity_needed = ingredient.quantity * meal_item.servings

                    if key in ingredient_map:
                        ingredient_map[key]["quantity"] += quantity_needed
                    else:
                        ingredient_map[key] = {
                            "item_name": ingredient.ingredient_name,
                            "quantity": quantity_needed,
                            "unit": ingredient.unit,
                            "category_id": ingredient.category_id,
                        }

        # Get user's inventory if excluding items
        items_excluded = 0
        if request.exclude_inventory_items:
            logger.info("Checking inventory to exclude existing items")

            inventory_items, _ = await inventory_repository.get_by_user(
                db=db,
                user_id=user_id,
                limit=1000,  # Get all inventory items
            )

            # Create inventory lookup by name
            inventory_lookup = {
                item.name.lower(): item for item in inventory_items
            }

            # Filter out items in inventory with sufficient quantity
            filtered_map = {}
            for key, value in ingredient_map.items():
                item_name_lower = value["item_name"].lower()

                if item_name_lower in inventory_lookup:
                    inventory_item = inventory_lookup[item_name_lower]

                    # Check if inventory has enough (considering unit conversion)
                    if (
                        inventory_item.unit == value["unit"]
                        and inventory_item.quantity >= value["quantity"]
                    ):
                        items_excluded += 1
                        logger.debug(
                            f"Excluding {value['item_name']} - "
                            f"sufficient in inventory"
                        )
                        continue

                    # If partial quantity available, reduce needed amount
                    if inventory_item.unit == value["unit"]:
                        value["quantity"] -= inventory_item.quantity
                        value["quantity"] = max(0, value["quantity"])

                filtered_map[key] = value

            ingredient_map = filtered_map

        # Create grocery list
        list_name = request.name or f"Grocery List for {meal_plan.name}"
        grocery_list_dict = {
            "user_id": user_id,
            "meal_plan_id": request.meal_plan_id,
            "name": list_name,
            "status": "active",
        }

        grocery_list = await grocery_list_repository.create(db, grocery_list_dict)

        # Create grocery list items
        items_data = []
        order_index = 0

        for value in ingredient_map.values():
            items_data.append(
                {
                    "item_name": value["item_name"],
                    "quantity": value["quantity"],
                    "unit": value["unit"],
                    "category_id": value.get("category_id"),
                    "is_checked": False,
                    "order_index": order_index,
                }
            )
            order_index += 1

        if items_data:
            await grocery_list_item_repository.bulk_create(
                db, grocery_list.id, items_data
            )

        await db.commit()

        # Reload with items
        grocery_list_full = await grocery_list_repository.get_by_id_and_user(
            db, grocery_list.id, user_id
        )

        logger.info(
            f"Grocery list generated with {len(items_data)} items, "
            f"{items_excluded} items excluded from inventory"
        )

        return {
            "grocery_list": grocery_list_full,
            "items_excluded": items_excluded,
            "message": (
                f"Grocery list generated with {len(items_data)} items. "
                f"{items_excluded} items excluded (already in inventory)."
                if request.exclude_inventory_items
                else f"Grocery list generated with {len(items_data)} items."
            ),
        }

    async def check_item(
        self,
        db: AsyncSession,
        grocery_list_id: int,
        item_id: int,
        user_id: int,
        is_checked: bool,
    ) -> GroceryListItem:
        """
        Check or uncheck a grocery list item.

        Args:
            db: Database session
            grocery_list_id: Grocery list ID
            item_id: Grocery list item ID
            user_id: User ID
            is_checked: Whether the item is checked

        Returns:
            Updated grocery list item

        Raises:
            HTTPException: If grocery list or item not found, or access denied
        """
        logger.info(
            f"Checking item {item_id} in list {grocery_list_id}, "
            f"checked={is_checked}"
        )

        # Verify grocery list ownership
        grocery_list = await grocery_list_repository.get_by_id_and_user(
            db, grocery_list_id, user_id
        )
        if not grocery_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grocery list not found",
            )

        # Get and update item
        item = await grocery_list_item_repository.get(db, item_id)
        if not item or item.grocery_list_id != grocery_list_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grocery list item not found",
            )

        item = await grocery_list_item_repository.check_item(db, item_id, is_checked)

        await db.commit()
        await db.refresh(item)

        logger.info(f"Item {item_id} {'checked' if is_checked else 'unchecked'}")
        return item


# Singleton instance
grocery_list_service = GroceryListService()
