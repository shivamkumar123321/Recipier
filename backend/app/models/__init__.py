"""
Database models package.

Imports all models for easy access and Alembic auto-discovery.
"""

from app.models.activity import ActivityLog
from app.models.grocery import GroceryList, GroceryListItem
from app.models.inventory import FoodCategory, InventoryItem
from app.models.meal import AIAnalysis, Meal, MealItem
from app.models.meal_plan import MealPlan, MealPlanItem
from app.models.recipe import Recipe, RecipeIngredient, RecipeInstruction, UserRecipe
from app.models.user import User, UserGoal, UserProfile

# Export all models
__all__ = [
    # User models
    "User",
    "UserProfile",
    "UserGoal",
    # Meal models
    "Meal",
    "MealItem",
    "AIAnalysis",
    # Inventory models
    "FoodCategory",
    "InventoryItem",
    # Recipe models
    "Recipe",
    "RecipeIngredient",
    "RecipeInstruction",
    "UserRecipe",
    # Meal plan models
    "MealPlan",
    "MealPlanItem",
    # Grocery models
    "GroceryList",
    "GroceryListItem",
    # Activity models
    "ActivityLog",
]
