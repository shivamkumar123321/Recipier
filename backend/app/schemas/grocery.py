"""
Grocery list-related Pydantic schemas for request/response validation.
"""

from typing import List, Optional

from pydantic import Field

from app.schemas.base import BaseSchema, TimestampSchema


# GroceryList Schemas
class GroceryListBase(BaseSchema):
    """Base grocery list schema."""

    name: str = Field(..., min_length=1, max_length=255)
    status: str = Field(
        default="active",
        pattern="^(active|completed|archived)$",
    )


class GroceryListCreate(GroceryListBase):
    """Schema for creating grocery list."""

    meal_plan_id: Optional[int] = None


class GroceryListUpdate(BaseSchema):
    """Schema for updating grocery list."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(
        None,
        pattern="^(active|completed|archived)$",
    )


class GroceryListResponse(GroceryListBase, TimestampSchema):
    """Schema for grocery list responses."""

    id: int
    user_id: int
    meal_plan_id: Optional[int] = None


# GroceryListItem Schemas
class GroceryListItemBase(BaseSchema):
    """Base grocery list item schema."""

    item_name: str = Field(..., min_length=1, max_length=255)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50)
    is_checked: bool = False
    estimated_price: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    order_index: int = Field(..., ge=0)


class GroceryListItemCreate(GroceryListItemBase):
    """Schema for creating grocery list item."""

    category_id: Optional[int] = None


class GroceryListItemUpdate(BaseSchema):
    """Schema for updating grocery list item."""

    item_name: Optional[str] = Field(None, min_length=1, max_length=255)
    category_id: Optional[int] = None
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    is_checked: Optional[bool] = None
    estimated_price: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0)


class GroceryListItemResponse(GroceryListItemBase, TimestampSchema):
    """Schema for grocery list item responses."""

    id: int
    grocery_list_id: int
    category_id: Optional[int] = None


# Combined GroceryList Response
class GroceryListFullResponse(GroceryListResponse):
    """Complete grocery list response with items."""

    items: List[GroceryListItemResponse] = Field(default_factory=list)


# Grocery List Pagination
class GroceryListListResponse(BaseSchema):
    """Schema for paginated grocery list."""

    items: List[GroceryListFullResponse]
    total: int
    skip: int
    limit: int


# Grocery List Generation from Meal Plan
class GroceryListGenerateRequest(BaseSchema):
    """Schema for generating grocery list from meal plan."""

    meal_plan_id: int = Field(
        ...,
        description="ID of the meal plan to generate grocery list from",
    )
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Name for the grocery list (auto-generated if not provided)",
    )
    exclude_inventory_items: bool = Field(
        default=True,
        description="Exclude items already in inventory",
    )


class GroceryListGenerateResponse(BaseSchema):
    """Schema for grocery list generation response."""

    grocery_list: GroceryListFullResponse
    items_excluded: int = Field(
        ...,
        description="Number of items excluded (already in inventory)",
    )
    message: str


# Grocery List Item Check
class GroceryListItemCheckRequest(BaseSchema):
    """Schema for checking/unchecking a grocery list item."""

    is_checked: bool = Field(
        ...,
        description="Whether the item is checked",
    )


class GroceryListItemCheckResponse(BaseSchema):
    """Schema for grocery list item check response."""

    item: GroceryListItemResponse
    message: str
