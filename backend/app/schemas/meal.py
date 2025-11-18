"""
Meal-related Pydantic schemas for request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from app.schemas.base import BaseSchema, SoftDeleteSchema, TimestampSchema


# Meal Schemas
class MealBase(BaseSchema):
    """Base meal schema."""

    name: str = Field(..., min_length=1, max_length=255)
    meal_type: Optional[str] = Field(
        None,
        pattern="^(breakfast|lunch|dinner|snack)$",
    )
    description: Optional[str] = None
    consumed_at: datetime


class MealCreate(MealBase):
    """Schema for creating a meal."""

    input_method: str = Field(..., pattern="^(text|voice|image)$")
    image_url: Optional[str] = None
    voice_transcript: Optional[str] = None
    total_calories: Optional[float] = Field(None, ge=0)
    macros: Optional[Dict[str, float]] = None
    micronutrients: Optional[Dict[str, Any]] = None


class MealUpdate(BaseSchema):
    """Schema for updating a meal."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    meal_type: Optional[str] = Field(
        None,
        pattern="^(breakfast|lunch|dinner|snack)$",
    )
    description: Optional[str] = None
    consumed_at: Optional[datetime] = None
    total_calories: Optional[float] = Field(None, ge=0)
    macros: Optional[Dict[str, float]] = None
    micronutrients: Optional[Dict[str, Any]] = None


class MealResponse(MealBase, TimestampSchema, SoftDeleteSchema):
    """Schema for meal responses."""

    id: int
    user_id: int
    input_method: str
    image_url: Optional[str] = None
    voice_transcript: Optional[str] = None
    total_calories: Optional[float] = None
    macros: Optional[Dict[str, float]] = None
    micronutrients: Optional[Dict[str, Any]] = None


# MealItem Schemas
class MealItemBase(BaseSchema):
    """Base meal item schema."""

    food_name: str = Field(..., min_length=1, max_length=255)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50)
    calories: Optional[float] = Field(None, ge=0)
    nutrition_data: Optional[Dict[str, Any]] = None


class MealItemCreate(MealItemBase):
    """Schema for creating a meal item."""

    pass


class MealItemUpdate(BaseSchema):
    """Schema for updating a meal item."""

    food_name: Optional[str] = Field(None, min_length=1, max_length=255)
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    calories: Optional[float] = Field(None, ge=0)
    nutrition_data: Optional[Dict[str, Any]] = None


class MealItemResponse(MealItemBase, TimestampSchema):
    """Schema for meal item responses."""

    id: int
    meal_id: int


# AIAnalysis Schemas
class AIAnalysisBase(BaseSchema):
    """Base AI analysis schema."""

    analysis: Optional[str] = None
    recommendations: Optional[str] = None
    nutrition_breakdown: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    model_version: Optional[str] = None


class AIAnalysisCreate(AIAnalysisBase):
    """Schema for creating AI analysis."""

    meal_id: int


class AIAnalysisResponse(AIAnalysisBase, TimestampSchema):
    """Schema for AI analysis responses."""

    id: int
    meal_id: int


# Combined Meal Response with Items and Analysis
class MealFullResponse(MealResponse):
    """Complete meal response with items and AI analysis."""

    meal_items: List[MealItemResponse] = Field(default_factory=list)
    ai_analysis: Optional[AIAnalysisResponse] = None
