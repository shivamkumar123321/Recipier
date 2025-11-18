"""
Meal plan-related Pydantic schemas for request/response validation.
"""

from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator

from app.schemas.base import BaseSchema, TimestampSchema


# MealPlan Schemas
class MealPlanBase(BaseSchema):
    """Base meal plan schema."""

    name: str = Field(..., min_length=1, max_length=255)
    start_date: date
    end_date: date
    target_calories: Optional[int] = Field(None, gt=0)
    macro_targets: Optional[Dict[str, float]] = None
    status: str = Field(
        default="active",
        pattern="^(active|completed|archived)$",
    )

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: date, info) -> date:
        """Ensure end_date is after start_date."""
        if "start_date" in info.data:
            start_date = info.data["start_date"]
            if v <= start_date:
                raise ValueError("end_date must be after start_date")
        return v


class MealPlanCreate(MealPlanBase):
    """Schema for creating meal plan."""

    pass


class MealPlanUpdate(BaseSchema):
    """Schema for updating meal plan."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    end_date: Optional[date] = None
    target_calories: Optional[int] = Field(None, gt=0)
    macro_targets: Optional[Dict[str, float]] = None
    status: Optional[str] = Field(
        None,
        pattern="^(active|completed|archived)$",
    )


class MealPlanResponse(MealPlanBase, TimestampSchema):
    """Schema for meal plan responses."""

    id: int
    user_id: int


# MealPlanItem Schemas
class MealPlanItemBase(BaseSchema):
    """Base meal plan item schema."""

    scheduled_date: date
    meal_type: str = Field(..., pattern="^(breakfast|lunch|dinner|snack)$")
    servings: int = Field(default=1, gt=0)
    notes: Optional[str] = None
    is_completed: bool = False


class MealPlanItemCreate(MealPlanItemBase):
    """Schema for creating meal plan item."""

    recipe_id: Optional[int] = None


class MealPlanItemUpdate(BaseSchema):
    """Schema for updating meal plan item."""

    recipe_id: Optional[int] = None
    scheduled_date: Optional[date] = None
    meal_type: Optional[str] = Field(None, pattern="^(breakfast|lunch|dinner|snack)$")
    servings: Optional[int] = Field(None, gt=0)
    notes: Optional[str] = None
    is_completed: Optional[bool] = None


class MealPlanItemResponse(MealPlanItemBase, TimestampSchema):
    """Schema for meal plan item responses."""

    id: int
    meal_plan_id: int
    recipe_id: Optional[int] = None


# Combined MealPlan Response
class MealPlanFullResponse(MealPlanResponse):
    """Complete meal plan response with items."""

    meal_plan_items: List[MealPlanItemResponse] = Field(default_factory=list)
