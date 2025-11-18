"""
Nutrition coaching schemas for request/response validation.
"""

from typing import List, Optional

from pydantic import Field

from app.schemas.base import BaseSchema


# Recipe Suggestion (from inventory)
class RecipeSuggestionFromInventory(BaseSchema):
    """Schema for recipe suggestion based on inventory."""

    recipe_name: str = Field(..., description="Name of the recipe")
    description: str = Field(..., description="Brief description")
    using_from_inventory: List[str] = Field(
        ...,
        description="Ingredients using from user's inventory",
    )
    additional_needed: List[str] = Field(
        default_factory=list,
        description="Additional ingredients needed",
    )
    meal_types: List[str] = Field(
        ...,
        description="Applicable meal types (breakfast, lunch, dinner, snack)",
    )
    prep_time_minutes: int = Field(..., description="Preparation time in minutes")
    why_recommended: str = Field(
        ...,
        description="Why this recipe is recommended for the user",
    )


# Coaching Advice
class CoachingAdviceRequest(BaseSchema):
    """Schema for requesting coaching advice."""

    specific_question: Optional[str] = Field(
        None,
        description="Optional specific question from user",
    )


class RecipeSuggestionInAdvice(BaseSchema):
    """Recipe suggestion within coaching advice."""

    name: str
    why: str = Field(..., description="Why this recipe fits user's goals")
    using_inventory: List[str] = Field(
        ...,
        description="Items from inventory used in recipe",
    )


class CoachingAdviceResponse(BaseSchema):
    """Schema for coaching advice response."""

    coaching_message: str = Field(
        ...,
        description="Main personalized coaching message",
    )
    quick_tips: List[str] = Field(
        ...,
        description="Quick actionable tips",
    )
    recipe_suggestions: List[RecipeSuggestionInAdvice] = Field(
        default_factory=list,
        description="Recipe suggestions based on inventory",
    )
    motivation: str = Field(
        ...,
        description="Motivating closing message",
    )


# Proactive Suggestions
class ProactiveSuggestionsResponse(BaseSchema):
    """Schema for proactive suggestions based on inventory."""

    urgency: str = Field(
        ...,
        pattern="^(low|medium|high)$",
        description="Urgency level of the suggestion",
    )
    primary_suggestion: str = Field(
        ...,
        description="Main action user should take",
    )
    reasons: List[str] = Field(
        ...,
        description="Reasons for this suggestion",
    )
    action_steps: List[str] = Field(
        ...,
        description="Specific steps to take",
    )
    recipes_to_try: List[dict] = Field(
        default_factory=list,
        description="Recommended recipes to try",
    )


# Recipe Generation from Inventory
class RecipeFromInventoryRequest(BaseSchema):
    """Schema for requesting recipes from inventory."""

    meal_type: Optional[str] = Field(
        None,
        pattern="^(breakfast|lunch|dinner|snack)$",
        description="Optional meal type filter",
    )
    max_suggestions: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of recipe suggestions",
    )


class RecipeFromInventoryResponse(BaseSchema):
    """Schema for recipe suggestions from inventory."""

    recipes: List[RecipeSuggestionFromInventory] = Field(
        ...,
        description="List of recipe suggestions",
    )
    total_inventory_items: int = Field(
        ...,
        description="Total items in user's inventory",
    )
    message: str = Field(
        ...,
        description="Summary message",
    )


# Custom Recipe Generation
class CustomRecipeGenerateRequest(BaseSchema):
    """Schema for generating custom recipe."""

    available_ingredients: List[str] = Field(
        ...,
        min_items=1,
        description="List of available ingredient names",
    )
    dietary_restrictions: Optional[List[str]] = Field(
        None,
        description="Dietary restrictions to respect",
    )
    cuisine_type: Optional[str] = Field(
        None,
        description="Desired cuisine type (italian, mexican, asian, etc.)",
    )
    meal_type: str = Field(
        default="dinner",
        pattern="^(breakfast|lunch|dinner|snack)$",
        description="Meal type for the recipe",
    )


class RecipeIngredient(BaseSchema):
    """Recipe ingredient with details."""

    name: str
    quantity: float
    unit: str
    from_inventory: bool = Field(
        ...,
        description="Whether ingredient is from user's inventory",
    )


class RecipeNutrition(BaseSchema):
    """Nutritional information per serving."""

    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float


class CustomRecipeResponse(BaseSchema):
    """Schema for custom generated recipe."""

    recipe_name: str
    description: str
    servings: int
    ingredients: List[RecipeIngredient]
    instructions: List[str] = Field(
        ...,
        description="Step-by-step cooking instructions",
    )
    nutrition_per_serving: RecipeNutrition
    prep_time_minutes: int
    cook_time_minutes: int
    difficulty: str = Field(
        ...,
        pattern="^(easy|medium|hard)$",
    )
    cuisine_type: Optional[str] = None
    meal_type: List[str] = Field(
        ...,
        description="Applicable meal types",
    )
