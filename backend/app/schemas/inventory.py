"""
Inventory-related Pydantic schemas for request/response validation.
"""

from datetime import date
from typing import Any, Dict, Optional

from pydantic import Field

from app.schemas.base import BaseSchema, SoftDeleteSchema, TimestampSchema


# FoodCategory Schemas
class FoodCategoryBase(BaseSchema):
    """Base food category schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)


class FoodCategoryCreate(FoodCategoryBase):
    """Schema for creating food category."""

    pass


class FoodCategoryUpdate(BaseSchema):
    """Schema for updating food category."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)


class FoodCategoryResponse(FoodCategoryBase, TimestampSchema):
    """Schema for food category responses."""

    id: int


# InventoryItem Schemas
class InventoryItemBase(BaseSchema):
    """Base inventory item schema."""

    name: str = Field(..., min_length=1, max_length=255)
    quantity: float = Field(..., ge=0)
    unit: str = Field(..., min_length=1, max_length=50)
    expiration_date: Optional[date] = None
    storage_location: Optional[str] = Field(
        None,
        pattern="^(pantry|fridge|freezer)$",
    )
    barcode: Optional[str] = Field(None, max_length=100)
    nutrition_per_unit: Optional[Dict[str, Any]] = None


class InventoryItemCreate(InventoryItemBase):
    """Schema for creating inventory item."""

    category_id: Optional[int] = None


class InventoryItemUpdate(BaseSchema):
    """Schema for updating inventory item."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category_id: Optional[int] = None
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    expiration_date: Optional[date] = None
    storage_location: Optional[str] = Field(
        None,
        pattern="^(pantry|fridge|freezer)$",
    )
    barcode: Optional[str] = Field(None, max_length=100)
    nutrition_per_unit: Optional[Dict[str, Any]] = None


class InventoryItemResponse(InventoryItemBase, TimestampSchema, SoftDeleteSchema):
    """Schema for inventory item responses."""

    id: int
    user_id: int
    category_id: Optional[int] = None
    category: Optional[FoodCategoryResponse] = None
