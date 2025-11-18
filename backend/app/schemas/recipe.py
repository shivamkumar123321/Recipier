"""
Recipe-related Pydantic schemas for request/response validation.
"""

from typing import Any, Dict, List, Optional

from pydantic import Field

from app.schemas.base import BaseSchema, SoftDeleteSchema, TimestampSchema


# Recipe Schemas
class RecipeBase(BaseSchema):
    """Base recipe schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    prep_time_minutes: Optional[int] = Field(None, ge=0)
    cook_time_minutes: Optional[int] = Field(None, ge=0)
    servings: int = Field(..., gt=0)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    image_url: Optional[str] = None
    calories_per_serving: Optional[float] = Field(None, ge=0)
    macros_per_serving: Optional[Dict[str, float]] = None
    is_public: bool = False


class RecipeCreate(RecipeBase):
    """Schema for creating recipe."""

    pass


class RecipeUpdate(BaseSchema):
    """Schema for updating recipe."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    prep_time_minutes: Optional[int] = Field(None, ge=0)
    cook_time_minutes: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, gt=0)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    image_url: Optional[str] = None
    calories_per_serving: Optional[float] = Field(None, ge=0)
    macros_per_serving: Optional[Dict[str, float]] = None
    is_public: Optional[bool] = None


class RecipeResponse(RecipeBase, TimestampSchema, SoftDeleteSchema):
    """Schema for recipe responses."""

    id: int
    user_id: Optional[int] = None
    views_count: int
    saves_count: int


# RecipeIngredient Schemas
class RecipeIngredientBase(BaseSchema):
    """Base recipe ingredient schema."""

    ingredient_name: str = Field(..., min_length=1, max_length=255)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50)
    is_optional: bool = False
    order_index: int = Field(..., ge=0)


class RecipeIngredientCreate(RecipeIngredientBase):
    """Schema for creating recipe ingredient."""

    category_id: Optional[int] = None


class RecipeIngredientResponse(RecipeIngredientBase, TimestampSchema):
    """Schema for recipe ingredient responses."""

    id: int
    recipe_id: int
    category_id: Optional[int] = None


# RecipeInstruction Schemas
class RecipeInstructionBase(BaseSchema):
    """Base recipe instruction schema."""

    step_number: int = Field(..., ge=1)
    instruction: str = Field(..., min_length=1)
    duration_minutes: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None


class RecipeInstructionCreate(RecipeInstructionBase):
    """Schema for creating recipe instruction."""

    pass


class RecipeInstructionResponse(RecipeInstructionBase, TimestampSchema):
    """Schema for recipe instruction responses."""

    id: int
    recipe_id: int


# UserRecipe Schemas
class UserRecipeBase(BaseSchema):
    """Base user recipe schema."""

    notes: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


class UserRecipeCreate(UserRecipeBase):
    """Schema for saving a recipe."""

    recipe_id: int


class UserRecipeUpdate(UserRecipeBase):
    """Schema for updating saved recipe."""

    pass


class UserRecipeResponse(UserRecipeBase, TimestampSchema):
    """Schema for user recipe responses."""

    id: int
    user_id: int
    recipe_id: int


# Combined Recipe Response
class RecipeFullResponse(RecipeResponse):
    """Complete recipe response with ingredients and instructions."""

    ingredients: List[RecipeIngredientResponse] = Field(default_factory=list)
    instructions: List[RecipeInstructionResponse] = Field(default_factory=list)
