"""
Inventory-related Pydantic schemas for request/response validation.
"""

from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator

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
    quantity: float = Field(..., gt=0, description="Quantity must be greater than 0")
    unit: str = Field(..., min_length=1, max_length=50)
    expiration_date: Optional[date] = None
    storage_location: Optional[str] = Field(
        None,
        pattern="^(pantry|fridge|freezer)$",
    )
    barcode: Optional[str] = Field(None, max_length=100)
    nutrition_per_unit: Optional[Dict[str, Any]] = None

    @field_validator("expiration_date")
    @classmethod
    def validate_expiration_date(cls, v: Optional[date]) -> Optional[date]:
        """Ensure expiration date is not in the past."""
        if v and v < date.today():
            raise ValueError("Expiration date cannot be in the past")
        return v


class InventoryItemCreate(InventoryItemBase):
    """Schema for creating inventory item."""

    category_id: Optional[int] = None


class InventoryItemUpdate(BaseSchema):
    """Schema for updating inventory item."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category_id: Optional[int] = None
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    expiration_date: Optional[date] = None
    storage_location: Optional[str] = Field(
        None,
        pattern="^(pantry|fridge|freezer)$",
    )
    barcode: Optional[str] = Field(None, max_length=100)
    nutrition_per_unit: Optional[Dict[str, Any]] = None

    @field_validator("expiration_date")
    @classmethod
    def validate_expiration_date(cls, v: Optional[date]) -> Optional[date]:
        """Ensure expiration date is not in the past."""
        if v and v < date.today():
            raise ValueError("Expiration date cannot be in the past")
        return v


class InventoryItemResponse(InventoryItemBase, TimestampSchema, SoftDeleteSchema):
    """Schema for inventory item responses."""

    id: int
    user_id: int
    category_id: Optional[int] = None
    category: Optional[FoodCategoryResponse] = None


class InventoryItemListResponse(BaseSchema):
    """Schema for paginated inventory item list."""

    items: List[InventoryItemResponse]
    total: int
    skip: int
    limit: int


# Voice Add Schema
class VoiceAddRequest(BaseSchema):
    """Schema for adding items via voice transcription."""

    audio_data: str = Field(
        ...,
        description="Base64 encoded audio data",
    )
    audio_format: str = Field(
        default="webm",
        pattern="^(webm|mp3|wav|m4a)$",
        description="Audio format (webm, mp3, wav, m4a)",
    )


class VoiceAddResponse(BaseSchema):
    """Schema for voice add response."""

    transcription: str = Field(..., description="Transcribed text from audio")
    items_added: List[InventoryItemResponse] = Field(
        ...,
        description="List of inventory items added",
    )
    message: str


# Image Scan Schema
class ImageScanRequest(BaseSchema):
    """Schema for adding items via image recognition."""

    image_data: str = Field(
        ...,
        description="Base64 encoded image data",
    )
    image_format: str = Field(
        default="jpeg",
        pattern="^(jpeg|jpg|png|webp)$",
        description="Image format",
    )


class ImageScanResponse(BaseSchema):
    """Schema for image scan response."""

    description: str = Field(..., description="AI description of the image")
    items_identified: List[str] = Field(
        ...,
        description="List of items identified in the image",
    )
    items_added: List[InventoryItemResponse] = Field(
        ...,
        description="List of inventory items added",
    )
    message: str


# Filter and Search Schemas
class InventoryFilterParams(BaseSchema):
    """Schema for inventory filtering parameters."""

    category_id: Optional[int] = None
    storage_location: Optional[str] = Field(
        None,
        pattern="^(pantry|fridge|freezer)$",
    )
    expiring_soon_days: Optional[int] = Field(
        None,
        ge=1,
        le=90,
        description="Get items expiring within N days",
    )
    expiration_from: Optional[date] = None
    expiration_to: Optional[date] = None
    search: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Search by item name",
    )
    sort_by: Optional[str] = Field(
        default="created_at",
        pattern="^(created_at|name|quantity|expiration_date)$",
        description="Field to sort by",
    )
    sort_order: Optional[str] = Field(
        default="desc",
        pattern="^(asc|desc)$",
        description="Sort order (asc/desc)",
    )


# Category Summary Schema
class CategorySummary(BaseSchema):
    """Schema for category-grouped inventory summary."""

    category_id: Optional[int]
    category_name: Optional[str]
    item_count: int
    total_items: int  # Total number of individual items (considering quantity)
    items: List[InventoryItemResponse]
