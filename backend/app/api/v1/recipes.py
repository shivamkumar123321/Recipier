"""
Recipe API endpoints.

Provides endpoints for recipe search, details, and favorites.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.logging import get_logger
from app.models.user import User
from app.schemas.coaching import (
    CustomRecipeGenerateRequest,
    CustomRecipeResponse,
)
from app.schemas.recipe import (
    RecipeListResponse,
    RecipeResponse,
    UserRecipeCreate,
    UserRecipeResponse,
)
from app.services.intelligent_meal_plan_service import (
    get_intelligent_meal_plan_service,
)
from app.services.openai_service import OpenAIServiceError
from app.services.recipe_service import recipe_service

logger = get_logger(__name__)

router = APIRouter()


@router.get("/search", response_model=RecipeListResponse)
async def search_recipes(
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    difficulty: Optional[str] = Query(None, regex="^(easy|medium|hard)$"),
    max_prep_time: Optional[int] = Query(None, ge=0),
    max_cook_time: Optional[int] = Query(None, ge=0),
    max_calories: Optional[int] = Query(None, ge=0),
    is_public: Optional[bool] = Query(None),
    include_user_recipes: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    sort_by: str = Query(
        "created_at",
        regex="^(created_at|name|prep_time_minutes|cook_time_minutes|calories_per_serving|views_count|saves_count)$",
    ),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Search recipes with comprehensive filtering.

    Filters:
    - **search**: Search by recipe name or description
    - **difficulty**: Filter by difficulty level (easy/medium/hard)
    - **max_prep_time**: Maximum prep time in minutes
    - **max_cook_time**: Maximum cook time in minutes
    - **max_calories**: Maximum calories per serving
    - **is_public**: Filter by public/private recipes
    - **include_user_recipes**: Include user's own recipes (default: true)

    Sorting:
    - **sort_by**: Field to sort by
    - **sort_order**: Sort order (asc/desc)

    Pagination:
    - **skip**: Number of records to skip (offset)
    - **limit**: Maximum number of records to return (max: 100)
    """
    logger.info(
        f"Recipe search request from user {current_user.id}: "
        f"search={search}, difficulty={difficulty}"
    )

    recipes, total = await recipe_service.search_recipes(
        db=db,
        user_id=current_user.id,
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

    return RecipeListResponse(
        items=[RecipeResponse.model_validate(r) for r in recipes],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get recipe details by ID.

    This endpoint:
    - Returns full recipe details including ingredients and instructions
    - Increments the recipe's view count
    - Requires authentication
    """
    logger.info(f"Get recipe request: recipe_id={recipe_id}, user={current_user.id}")

    recipe = await recipe_service.get_recipe_by_id(
        db=db,
        recipe_id=recipe_id,
        increment_views=True,
    )

    return RecipeResponse.model_validate(recipe)


@router.post("/favorites", response_model=UserRecipeResponse, status_code=status.HTTP_201_CREATED)
async def save_recipe_to_favorites(
    user_recipe_data: UserRecipeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Save a recipe to user's favorites.

    This endpoint:
    - Adds the recipe to user's saved recipes
    - Increments the recipe's save count
    - Allows optional notes and rating (1-5 stars)

    Request body:
    - **recipe_id**: ID of the recipe to save
    - **notes**: Optional notes about the recipe
    - **rating**: Optional rating (1-5 stars)
    """
    logger.info(
        f"Save recipe to favorites: recipe_id={user_recipe_data.recipe_id}, "
        f"user={current_user.id}"
    )

    user_recipe = await recipe_service.save_recipe(
        db=db,
        recipe_id=user_recipe_data.recipe_id,
        user_id=current_user.id,
        notes=user_recipe_data.notes,
        rating=user_recipe_data.rating,
    )

    return UserRecipeResponse.model_validate(user_recipe)


@router.delete("/favorites/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_recipe_from_favorites(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Remove a recipe from user's favorites.

    This endpoint:
    - Removes the recipe from user's saved recipes
    - Decrements the recipe's save count
    """
    logger.info(
        f"Remove recipe from favorites: recipe_id={recipe_id}, user={current_user.id}"
    )

    await recipe_service.unsave_recipe(
        db=db,
        recipe_id=recipe_id,
        user_id=current_user.id,
    )

    return None


@router.get("/favorites/my", response_model=RecipeListResponse)
async def get_my_favorite_recipes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get user's favorite recipes.

    Returns all recipes saved by the current user with pagination.

    Pagination:
    - **skip**: Number of records to skip (offset)
    - **limit**: Maximum number of records to return (max: 100)
    """
    logger.info(f"Get favorites request from user {current_user.id}")

    user_recipes, total = await recipe_service.get_user_favorites(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    # Extract recipes from user_recipes
    recipes = [ur.recipe for ur in user_recipes if ur.recipe]

    return RecipeListResponse(
        items=[RecipeResponse.model_validate(r) for r in recipes],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/generate",
    response_model=CustomRecipeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate custom recipe from ingredients",
    description="Generate a custom AI-powered recipe from available ingredients",
)
async def generate_custom_recipe(
    request: CustomRecipeGenerateRequest,
    current_user: User = Depends(get_current_active_user),
) -> CustomRecipeResponse:
    """
    Generate a custom recipe from specific ingredients using AI.

    **AI-Powered Recipe Generation:**
    The AI creates a complete, detailed recipe with:
    - Step-by-step cooking instructions
    - Nutritional information per serving
    - Cooking times and difficulty level
    - Suggestions for additional ingredients if needed

    **Features:**
    - **available_ingredients**: List of ingredients you have available
    - **dietary_restrictions**: Optional restrictions (vegetarian, gluten-free, etc.)
    - **cuisine_type**: Optional cuisine preference (italian, mexican, asian, etc.)
    - **meal_type**: Type of meal (breakfast, lunch, dinner, snack)

    **Example Request:**
    ```json
    {
      "available_ingredients": ["Chicken Breast", "Broccoli", "Garlic", "Olive Oil"],
      "dietary_restrictions": ["gluten-free"],
      "cuisine_type": "mediterranean",
      "meal_type": "dinner"
    }
    ```

    **Response Includes:**
    - Complete recipe with name and description
    - Ingredient list with quantities and units
    - Step-by-step instructions
    - Nutrition facts (calories, protein, carbs, fat)
    - Prep and cook times
    - Difficulty level

    Args:
        request: Custom recipe generation request with ingredients and preferences
        current_user: Current authenticated user

    Returns:
        Complete custom recipe with full details

    Raises:
        HTTPException: If recipe generation fails
    """
    logger.info(
        f"Custom recipe generation request from user {current_user.id}, "
        f"ingredients: {len(request.available_ingredients)}, "
        f"cuisine: {request.cuisine_type}, meal: {request.meal_type}"
    )

    try:
        # Get intelligent meal plan service
        meal_plan_service = get_intelligent_meal_plan_service()

        # Generate custom recipe
        recipe = await meal_plan_service.generate_custom_recipe(
            available_ingredients=request.available_ingredients,
            dietary_restrictions=request.dietary_restrictions,
            cuisine_type=request.cuisine_type,
            meal_type=request.meal_type,
        )

        logger.info(
            f"Custom recipe '{recipe.get('recipe_name')}' generated for user {current_user.id}"
        )

        return CustomRecipeResponse(**recipe)

    except OpenAIServiceError as e:
        logger.error(f"OpenAI service error during recipe generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Recipe generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate custom recipe",
        )
