"""
Vision-related Pydantic schemas for food image recognition.
"""

from typing import List, Optional

from pydantic import Field

from app.schemas.base import BaseSchema


# Food Item Identified in Image
class IdentifiedFoodItem(BaseSchema):
    """Schema for a food item identified in an image."""

    name: str = Field(..., description="Name of the food item")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0)",
    )
    quantity: Optional[float] = Field(
        None,
        description="Estimated quantity (if determinable)",
    )
    unit: Optional[str] = Field(
        None,
        description="Unit of measurement (items, lbs, oz, etc.)",
    )
    category: Optional[str] = Field(
        None,
        description="Food category (fruit, vegetable, protein, etc.)",
    )
    estimated_shelf_life_days: Optional[int] = Field(
        None,
        description="Estimated shelf life in days",
    )
    storage_location: Optional[str] = Field(
        None,
        description="Recommended storage location (pantry, fridge, freezer)",
    )


# Vision Identification Request/Response
class VisionIdentifyRequest(BaseSchema):
    """Schema for general-purpose food identification request."""

    image_data: str = Field(
        ...,
        description="Base64 encoded image data",
    )
    image_format: str = Field(
        default="jpeg",
        pattern="^(jpeg|jpg|png|webp)$",
        description="Image format",
    )
    include_nutrition: bool = Field(
        default=False,
        description="Include nutritional information in response",
    )


class VisionIdentifyResponse(BaseSchema):
    """Schema for vision identification response."""

    description: str = Field(
        ...,
        description="AI-generated description of the image",
    )
    items: List[IdentifiedFoodItem] = Field(
        ...,
        description="List of identified food items",
    )
    total_items_count: int = Field(
        ...,
        description="Total number of items identified",
    )
    image_quality: Optional[str] = Field(
        None,
        description="Image quality assessment (good, fair, poor)",
    )


# Vision File Upload Request/Response
class VisionFileUploadResponse(BaseSchema):
    """Response for vision file upload."""

    description: str
    items: List[IdentifiedFoodItem]
    total_items_count: int
    image_url: str = Field(..., description="URL to access the saved image")
    image_metadata: dict = Field(
        ...,
        description="Image metadata (width, height, size, format)",
    )
    processing_time_ms: float


# Nutrition Information (if requested)
class NutritionInfo(BaseSchema):
    """Nutritional information for identified food."""

    total_calories: Optional[int] = None
    total_protein_g: Optional[float] = None
    total_carbs_g: Optional[float] = None
    total_fat_g: Optional[float] = None
    total_fiber_g: Optional[float] = None
    items: List[dict] = Field(
        default_factory=list,
        description="Per-item nutrition breakdown",
    )


class VisionIdentifyWithNutritionResponse(VisionIdentifyResponse):
    """Vision identification response with nutrition information."""

    nutrition: Optional[NutritionInfo] = None
