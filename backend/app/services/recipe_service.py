"""
Recipe service for business logic.

Handles recipe search, creation, and user favorites.
"""

from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.recipe import Recipe, UserRecipe
from app.repositories.recipe_repository import (
    recipe_ingredient_repository,
    recipe_instruction_repository,
    recipe_repository,
    user_recipe_repository,
)
from app.schemas.recipe import (
    RecipeCreate,
    RecipeIngredientCreate,
    RecipeInstructionCreate,
)

logger = get_logger(__name__)


class RecipeService:
    """Service for recipe operations."""

    async def search_recipes(
        self,
        db: AsyncSession,
        user_id: Optional[int] = None,
        search: Optional[str] = None,
        difficulty: Optional[str] = None,
        max_prep_time: Optional[int] = None,
        max_cook_time: Optional[int] = None,
        max_calories: Optional[int] = None,
        is_public: Optional[bool] = None,
        include_user_recipes: bool = True,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Recipe], int]:
        """
        Search recipes with comprehensive filtering.

        Args:
            db: Database session
            user_id: User ID for filtering user's own recipes
            search: Search by recipe name or description
            difficulty: Filter by difficulty level
            max_prep_time: Maximum prep time in minutes
            max_cook_time: Maximum cook time in minutes
            max_calories: Maximum calories per serving
            is_public: Filter by public/private recipes
            include_user_recipes: Include user's own recipes
            skip: Number of records to skip
            limit: Maximum number of records to return
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)

        Returns:
            Tuple of (recipes list, total count)
        """
        logger.info(
            f"Searching recipes with filters: search={search}, "
            f"difficulty={difficulty}, user_id={user_id}"
        )

        recipes, total = await recipe_repository.search_recipes(
            db=db,
            user_id=user_id,
            search=search,
            difficulty=difficulty,
            max_prep_time=max_prep_time,
            max_cook_time=max_cook_time,
            max_calories=max_calories,
            is_public=is_public,
            include_user_recipes=include_user_recipes,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        logger.info(f"Found {total} recipes matching criteria")
        return recipes, total

    async def get_recipe_by_id(
        self,
        db: AsyncSession,
        recipe_id: int,
        increment_views: bool = True,
    ) -> Optional[Recipe]:
        """
        Get recipe by ID with details.

        Args:
            db: Database session
            recipe_id: Recipe ID
            increment_views: Whether to increment views count

        Returns:
            Recipe with ingredients and instructions if found, None otherwise

        Raises:
            HTTPException: If recipe not found
        """
        logger.info(f"Fetching recipe with ID: {recipe_id}")

        recipe = await recipe_repository.get_by_id_with_details(db, recipe_id)

        if not recipe:
            logger.warning(f"Recipe {recipe_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found",
            )

        # Increment views count
        if increment_views:
            await recipe_repository.increment_views(db, recipe_id)
            await db.commit()

        return recipe

    async def create_recipe(
        self,
        db: AsyncSession,
        recipe_data: RecipeCreate,
        ingredients: List[RecipeIngredientCreate],
        instructions: List[RecipeInstructionCreate],
        user_id: Optional[int] = None,
    ) -> Recipe:
        """
        Create a new recipe with ingredients and instructions.

        Args:
            db: Database session
            recipe_data: Recipe creation data
            ingredients: List of recipe ingredients
            instructions: List of recipe instructions
            user_id: User ID (None for public recipes)

        Returns:
            Created recipe with ingredients and instructions
        """
        logger.info(f"Creating recipe: {recipe_data.name}")

        # Create recipe
        recipe_dict = recipe_data.model_dump()
        recipe_dict["user_id"] = user_id
        recipe = await recipe_repository.create(db, recipe_dict)

        # Create ingredients
        if ingredients:
            ingredients_data = [ing.model_dump() for ing in ingredients]
            await recipe_ingredient_repository.bulk_create(
                db, recipe.id, ingredients_data
            )

        # Create instructions
        if instructions:
            instructions_data = [inst.model_dump() for inst in instructions]
            await recipe_instruction_repository.bulk_create(
                db, recipe.id, instructions_data
            )

        await db.commit()

        # Reload with details
        recipe_full = await recipe_repository.get_by_id_with_details(db, recipe.id)

        logger.info(f"Recipe created successfully: {recipe.id}")
        return recipe_full

    async def save_recipe(
        self,
        db: AsyncSession,
        recipe_id: int,
        user_id: int,
        notes: Optional[str] = None,
        rating: Optional[int] = None,
    ) -> UserRecipe:
        """
        Save a recipe to user's favorites.

        Args:
            db: Database session
            recipe_id: Recipe ID
            user_id: User ID
            notes: Optional notes
            rating: Optional rating (1-5)

        Returns:
            Created user recipe (favorite)

        Raises:
            HTTPException: If recipe not found or already saved
        """
        logger.info(f"User {user_id} saving recipe {recipe_id}")

        # Check if recipe exists
        recipe = await recipe_repository.get(db, recipe_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found",
            )

        # Check if already saved
        existing = await user_recipe_repository.get_by_user_and_recipe(
            db, user_id, recipe_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recipe already saved",
            )

        # Create user recipe
        user_recipe_data = {
            "user_id": user_id,
            "recipe_id": recipe_id,
            "notes": notes,
            "rating": rating,
        }
        user_recipe = await user_recipe_repository.create(db, user_recipe_data)

        # Increment saves count
        await recipe_repository.increment_saves(db, recipe_id)

        await db.commit()
        await db.refresh(user_recipe)

        logger.info(f"Recipe {recipe_id} saved to favorites")
        return user_recipe

    async def unsave_recipe(
        self,
        db: AsyncSession,
        recipe_id: int,
        user_id: int,
    ) -> bool:
        """
        Remove a recipe from user's favorites.

        Args:
            db: Database session
            recipe_id: Recipe ID
            user_id: User ID

        Returns:
            True if removed, False if not found

        Raises:
            HTTPException: If recipe not in favorites
        """
        logger.info(f"User {user_id} unsaving recipe {recipe_id}")

        user_recipe = await user_recipe_repository.get_by_user_and_recipe(
            db, user_id, recipe_id
        )

        if not user_recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not in favorites",
            )

        await user_recipe_repository.delete(db, user_recipe.id)

        # Decrement saves count
        await recipe_repository.decrement_saves(db, recipe_id)

        await db.commit()

        logger.info(f"Recipe {recipe_id} removed from favorites")
        return True

    async def get_user_favorites(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[UserRecipe], int]:
        """
        Get user's favorite recipes.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (user recipes list, total count)
        """
        logger.info(f"Fetching favorites for user {user_id}")

        user_recipes, total = await user_recipe_repository.get_favorites_by_user(
            db, user_id, skip, limit
        )

        logger.info(f"Found {total} favorite recipes")
        return user_recipes, total


# Singleton instance
recipe_service = RecipeService()
