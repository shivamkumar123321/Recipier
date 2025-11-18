"""
Grocery list API endpoints.

Provides endpoints for grocery list management and generation from meal plans.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.logging import get_logger
from app.models.user import User
from app.schemas.grocery import (
    GroceryListFullResponse,
    GroceryListGenerateRequest,
    GroceryListGenerateResponse,
    GroceryListItemCheckRequest,
    GroceryListItemCheckResponse,
    GroceryListItemResponse,
    GroceryListListResponse,
)
from app.services.grocery_list_service import grocery_list_service

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=GroceryListListResponse)
async def get_grocery_lists(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None, regex="^(active|completed|archived)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get user's grocery lists with optional filtering.

    Filters:
    - **status**: Filter by status (active/completed/archived)

    Pagination:
    - **skip**: Number of records to skip (offset)
    - **limit**: Maximum number of records to return (max: 100)
    """
    logger.info(
        f"Get grocery lists request from user {current_user.id}, status={status}"
    )

    grocery_lists, total = await grocery_list_service.get_user_grocery_lists(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
    )

    return GroceryListListResponse(
        items=[GroceryListFullResponse.model_validate(gl) for gl in grocery_lists],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/generate", response_model=GroceryListGenerateResponse, status_code=status.HTTP_201_CREATED)
async def generate_grocery_list_from_meal_plan(
    request: GroceryListGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate grocery list from a meal plan.

    This endpoint:
    1. Extracts all ingredients from meals in the meal plan
    2. Aggregates quantities for duplicate items
    3. Optionally excludes items already in user's inventory
    4. Creates a new grocery list with all items

    Request body:
    - **meal_plan_id**: ID of the meal plan to generate from
    - **name**: Optional name for the grocery list (auto-generated if not provided)
    - **exclude_inventory_items**: Exclude items already in inventory (default: true)

    Returns:
    - Created grocery list with all items
    - Number of items excluded from inventory
    - Success message
    """
    logger.info(
        f"Generate grocery list request from user {current_user.id}, "
        f"meal_plan_id={request.meal_plan_id}"
    )

    result = await grocery_list_service.generate_from_meal_plan(
        db=db,
        request=request,
        user_id=current_user.id,
    )

    return GroceryListGenerateResponse(
        grocery_list=GroceryListFullResponse.model_validate(result["grocery_list"]),
        items_excluded=result["items_excluded"],
        message=result["message"],
    )


@router.get("/{grocery_list_id}", response_model=GroceryListFullResponse)
async def get_grocery_list(
    grocery_list_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get specific grocery list with all items.

    Returns:
    - Complete grocery list details
    - All items in the list
    - Check status for each item
    """
    logger.info(
        f"Get grocery list request: grocery_list_id={grocery_list_id}, "
        f"user={current_user.id}"
    )

    grocery_list = await grocery_list_service.get_grocery_list_by_id(
        db=db,
        grocery_list_id=grocery_list_id,
        user_id=current_user.id,
    )

    return GroceryListFullResponse.model_validate(grocery_list)


@router.patch("/{grocery_list_id}/item/{item_id}", response_model=GroceryListItemCheckResponse)
async def check_grocery_list_item(
    grocery_list_id: int,
    item_id: int,
    request: GroceryListItemCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Check or uncheck a grocery list item.

    This endpoint allows users to mark items as checked/unchecked
    as they shop.

    Request body:
    - **is_checked**: Whether the item is checked (true/false)

    Returns:
    - Updated grocery list item
    - Success message
    """
    logger.info(
        f"Check grocery item request: list={grocery_list_id}, item={item_id}, "
        f"checked={request.is_checked}, user={current_user.id}"
    )

    item = await grocery_list_service.check_item(
        db=db,
        grocery_list_id=grocery_list_id,
        item_id=item_id,
        user_id=current_user.id,
        is_checked=request.is_checked,
    )

    return GroceryListItemCheckResponse(
        item=GroceryListItemResponse.model_validate(item),
        message=f"Item {'checked' if request.is_checked else 'unchecked'} successfully",
    )
