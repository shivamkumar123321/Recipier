"""
Meal plan API endpoints.

Provides endpoints for meal plan management and AI generation.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.logging import get_logger
from app.models.user import User
from app.schemas.meal_plan import (
    CookMealRequest,
    CookMealResponse,
    MealPlanFullResponse,
    MealPlanGenerateRequest,
    MealPlanGenerateResponse,
    MealPlanListResponse,
    MealPlanResponse,
)
from app.services.meal_plan_service import meal_plan_service

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=MealPlanListResponse)
async def get_meal_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None, regex="^(active|completed|archived)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get user's meal plans with optional filtering.

    Filters:
    - **status**: Filter by status (active/completed/archived)

    Pagination:
    - **skip**: Number of records to skip (offset)
    - **limit**: Maximum number of records to return (max: 100)
    """
    logger.info(f"Get meal plans request from user {current_user.id}, status={status}")

    meal_plans, total = await meal_plan_service.get_user_meal_plans(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
    )

    return MealPlanListResponse(
        items=[MealPlanResponse.model_validate(mp) for mp in meal_plans],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/generate", response_model=MealPlanGenerateResponse, status_code=status.HTTP_201_CREATED)
async def generate_ai_meal_plan(
    request: MealPlanGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate AI-powered meal plan based on preferences.

    **PLACEHOLDER**: This endpoint currently uses placeholder logic.
    In production, it will integrate with OpenAI GPT-4 to generate
    personalized meal plans based on:

    - **Dietary preferences** (vegetarian, vegan, gluten-free, etc.)
    - **Excluded ingredients** (allergies, dislikes)
    - **Nutritional targets** (calories, macros)
    - **Meal types** (breakfast, lunch, dinner, snacks)
    - **Date range** (start_date to end_date)

    The AI will:
    1. Select or create recipes matching preferences
    2. Balance nutrition across all meals
    3. Avoid excluded ingredients
    4. Consider seasonal availability
    5. Provide variety and meal rotation

    Request body:
    - **name**: Meal plan name
    - **start_date**: Start date
    - **end_date**: End date
    - **target_calories**: Optional daily calorie target
    - **macro_targets**: Optional macro targets (protein_g, carbs_g, fat_g)
    - **dietary_preferences**: Optional dietary preferences list
    - **excluded_ingredients**: Optional ingredients to exclude
    - **meal_types**: List of meal types to include (default: breakfast, lunch, dinner)
    """
    logger.info(
        f"Generate AI meal plan request from user {current_user.id}: {request.name}"
    )

    meal_plan = await meal_plan_service.generate_ai_meal_plan(
        db=db,
        request=request,
        user_id=current_user.id,
    )

    return MealPlanGenerateResponse(
        meal_plan=MealPlanFullResponse.model_validate(meal_plan),
        message=(
            "Meal plan generated successfully (PLACEHOLDER MODE). "
            "AI integration coming soon!"
        ),
    )


@router.get("/{meal_plan_id}", response_model=MealPlanFullResponse)
async def get_meal_plan(
    meal_plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get specific meal plan with all meals.

    Returns:
    - Complete meal plan details
    - All scheduled meals (meal plan items)
    - Linked recipes for each meal
    """
    logger.info(
        f"Get meal plan request: meal_plan_id={meal_plan_id}, user={current_user.id}"
    )

    meal_plan = await meal_plan_service.get_meal_plan_by_id(
        db=db,
        meal_plan_id=meal_plan_id,
        user_id=current_user.id,
    )

    return MealPlanFullResponse.model_validate(meal_plan)


@router.post("/{meal_plan_id}/cook", response_model=CookMealResponse)
async def cook_meal(
    meal_plan_id: int,
    request: CookMealRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Mark a meal as cooked and update inventory.

    This endpoint:
    1. Marks the meal plan item as completed
    2. Deducts recipe ingredients from user's inventory
    3. Returns summary of inventory changes

    Request body:
    - **meal_plan_item_id**: ID of the meal to mark as cooked

    Returns:
    - Updated meal plan item
    - Inventory update status
    - Number of items deducted from inventory
    """
    logger.info(
        f"Cook meal request: meal_plan={meal_plan_id}, "
        f"item={request.meal_plan_item_id}, user={current_user.id}"
    )

    result = await meal_plan_service.cook_meal(
        db=db,
        meal_plan_id=meal_plan_id,
        meal_plan_item_id=request.meal_plan_item_id,
        user_id=current_user.id,
    )

    return CookMealResponse(
        meal_plan_item=result["meal_plan_item"],
        inventory_updated=result["inventory_updated"],
        items_deducted=result["items_deducted"],
        message=result["message"],
    )
