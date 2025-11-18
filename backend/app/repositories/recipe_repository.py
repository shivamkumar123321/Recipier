"""
Recipe repository for database operations.

Provides data access layer for recipes and user recipes.
"""

from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.models.recipe import Recipe, RecipeIngredient, RecipeInstruction, UserRecipe
from app.repositories.base import BaseRepository

logger = get_logger(__name__)


class RecipeRepository(BaseRepository[Recipe]):
    """Repository for recipe operations."""

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
        Search recipes with comprehensive filtering and sorting.

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
        # Build base query
        conditions = [Recipe.deleted_at.is_(None)]

        # Public recipes or user's own recipes
        if is_public is not None:
            conditions.append(Recipe.is_public == is_public)
        elif user_id and include_user_recipes:
            conditions.append(
                or_(Recipe.is_public == True, Recipe.user_id == user_id)
            )
        elif not user_id:
            conditions.append(Recipe.is_public == True)

        # Search filter
        if search:
            conditions.append(
                or_(
                    Recipe.name.ilike(f"%{search}%"),
                    Recipe.description.ilike(f"%{search}%"),
                )
            )

        # Difficulty filter
        if difficulty:
            conditions.append(Recipe.difficulty == difficulty)

        # Time filters
        if max_prep_time is not None:
            conditions.append(Recipe.prep_time_minutes <= max_prep_time)

        if max_cook_time is not None:
            conditions.append(Recipe.cook_time_minutes <= max_cook_time)

        # Calories filter
        if max_calories is not None:
            conditions.append(Recipe.calories_per_serving <= max_calories)

        query = select(Recipe).where(and_(*conditions))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply sorting
        sort_column = getattr(Recipe, sort_by, Recipe.created_at)
        if sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        result = await db.execute(query)
        recipes = result.scalars().all()

        return list(recipes), total

    async def get_by_id_with_details(
        self,
        db: AsyncSession,
        recipe_id: int,
    ) -> Optional[Recipe]:
        """
        Get recipe by ID with ingredients and instructions.

        Args:
            db: Database session
            recipe_id: Recipe ID

        Returns:
            Recipe with ingredients and instructions if found, None otherwise
        """
        result = await db.execute(
            select(Recipe)
            .where(
                Recipe.id == recipe_id,
                Recipe.deleted_at.is_(None),
            )
            .options(
                selectinload(Recipe.ingredients),
                selectinload(Recipe.instructions),
            )
        )

        return result.scalar_one_or_none()

    async def increment_views(
        self,
        db: AsyncSession,
        recipe_id: int,
    ) -> None:
        """
        Increment views count for a recipe.

        Args:
            db: Database session
            recipe_id: Recipe ID
        """
        recipe = await self.get(db, recipe_id)
        if recipe:
            recipe.views_count += 1
            await db.flush()

    async def increment_saves(
        self,
        db: AsyncSession,
        recipe_id: int,
    ) -> None:
        """
        Increment saves count for a recipe.

        Args:
            db: Database session
            recipe_id: Recipe ID
        """
        recipe = await self.get(db, recipe_id)
        if recipe:
            recipe.saves_count += 1
            await db.flush()

    async def decrement_saves(
        self,
        db: AsyncSession,
        recipe_id: int,
    ) -> None:
        """
        Decrement saves count for a recipe.

        Args:
            db: Database session
            recipe_id: Recipe ID
        """
        recipe = await self.get(db, recipe_id)
        if recipe and recipe.saves_count > 0:
            recipe.saves_count -= 1
            await db.flush()


class RecipeIngredientRepository(BaseRepository[RecipeIngredient]):
    """Repository for recipe ingredient operations."""

    async def get_by_recipe(
        self,
        db: AsyncSession,
        recipe_id: int,
    ) -> List[RecipeIngredient]:
        """
        Get all ingredients for a recipe.

        Args:
            db: Database session
            recipe_id: Recipe ID

        Returns:
            List of recipe ingredients
        """
        result = await db.execute(
            select(RecipeIngredient)
            .where(RecipeIngredient.recipe_id == recipe_id)
            .order_by(RecipeIngredient.order_index)
        )

        return list(result.scalars().all())

    async def bulk_create(
        self,
        db: AsyncSession,
        recipe_id: int,
        ingredients_data: List[dict],
    ) -> List[RecipeIngredient]:
        """
        Create multiple recipe ingredients at once.

        Args:
            db: Database session
            recipe_id: Recipe ID
            ingredients_data: List of ingredient data dictionaries

        Returns:
            List of created recipe ingredients
        """
        ingredients = []
        for data in ingredients_data:
            data["recipe_id"] = recipe_id
            ingredient = RecipeIngredient(**data)
            db.add(ingredient)
            ingredients.append(ingredient)

        await db.flush()

        return ingredients


class RecipeInstructionRepository(BaseRepository[RecipeInstruction]):
    """Repository for recipe instruction operations."""

    async def get_by_recipe(
        self,
        db: AsyncSession,
        recipe_id: int,
    ) -> List[RecipeInstruction]:
        """
        Get all instructions for a recipe.

        Args:
            db: Database session
            recipe_id: Recipe ID

        Returns:
            List of recipe instructions
        """
        result = await db.execute(
            select(RecipeInstruction)
            .where(RecipeInstruction.recipe_id == recipe_id)
            .order_by(RecipeInstruction.step_number)
        )

        return list(result.scalars().all())

    async def bulk_create(
        self,
        db: AsyncSession,
        recipe_id: int,
        instructions_data: List[dict],
    ) -> List[RecipeInstruction]:
        """
        Create multiple recipe instructions at once.

        Args:
            db: Database session
            recipe_id: Recipe ID
            instructions_data: List of instruction data dictionaries

        Returns:
            List of created recipe instructions
        """
        instructions = []
        for data in instructions_data:
            data["recipe_id"] = recipe_id
            instruction = RecipeInstruction(**data)
            db.add(instruction)
            instructions.append(instruction)

        await db.flush()

        return instructions


class UserRecipeRepository(BaseRepository[UserRecipe]):
    """Repository for user recipe (favorites) operations."""

    async def get_by_user_and_recipe(
        self,
        db: AsyncSession,
        user_id: int,
        recipe_id: int,
    ) -> Optional[UserRecipe]:
        """
        Get user recipe by user ID and recipe ID.

        Args:
            db: Database session
            user_id: User ID
            recipe_id: Recipe ID

        Returns:
            User recipe if found, None otherwise
        """
        result = await db.execute(
            select(UserRecipe).where(
                UserRecipe.user_id == user_id,
                UserRecipe.recipe_id == recipe_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_favorites_by_user(
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
        query = (
            select(UserRecipe)
            .where(UserRecipe.user_id == user_id)
            .options(selectinload(UserRecipe.recipe))
            .order_by(UserRecipe.created_at.desc())
        )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        user_recipes = result.scalars().all()

        return list(user_recipes), total


# Singleton instances
recipe_repository = RecipeRepository(Recipe)
recipe_ingredient_repository = RecipeIngredientRepository(RecipeIngredient)
recipe_instruction_repository = RecipeInstructionRepository(RecipeInstruction)
user_recipe_repository = UserRecipeRepository(UserRecipe)
