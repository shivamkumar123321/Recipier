"""
Pydantic schemas package for request/response validation.
"""

from app.schemas.activity import (
    ActivityLogCreate,
    ActivityLogResponse,
)
from app.schemas.grocery import (
    GroceryListCreate,
    GroceryListFullResponse,
    GroceryListItemCreate,
    GroceryListItemResponse,
    GroceryListItemUpdate,
    GroceryListResponse,
    GroceryListUpdate,
)
from app.schemas.inventory import (
    FoodCategoryCreate,
    FoodCategoryResponse,
    FoodCategoryUpdate,
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryItemUpdate,
)
from app.schemas.meal import (
    AIAnalysisCreate,
    AIAnalysisResponse,
    MealCreate,
    MealFullResponse,
    MealItemCreate,
    MealItemResponse,
    MealItemUpdate,
    MealResponse,
    MealUpdate,
)
from app.schemas.meal_plan import (
    MealPlanCreate,
    MealPlanFullResponse,
    MealPlanItemCreate,
    MealPlanItemResponse,
    MealPlanItemUpdate,
    MealPlanResponse,
    MealPlanUpdate,
)
from app.schemas.recipe import (
    RecipeCreate,
    RecipeFullResponse,
    RecipeIngredientCreate,
    RecipeIngredientResponse,
    RecipeInstructionCreate,
    RecipeInstructionResponse,
    RecipeResponse,
    RecipeUpdate,
    UserRecipeCreate,
    UserRecipeResponse,
    UserRecipeUpdate,
)
from app.schemas.user import (
    TokenResponse,
    UserCreate,
    UserFullResponse,
    UserGoalCreate,
    UserGoalResponse,
    UserGoalUpdate,
    UserLogin,
    UserProfileCreate,
    UserProfileResponse,
    UserProfileUpdate,
    UserResponse,
    UserUpdate,
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserFullResponse",
    "UserLogin",
    "TokenResponse",
    "UserProfileCreate",
    "UserProfileUpdate",
    "UserProfileResponse",
    "UserGoalCreate",
    "UserGoalUpdate",
    "UserGoalResponse",
    # Meal schemas
    "MealCreate",
    "MealUpdate",
    "MealResponse",
    "MealFullResponse",
    "MealItemCreate",
    "MealItemUpdate",
    "MealItemResponse",
    "AIAnalysisCreate",
    "AIAnalysisResponse",
    # Inventory schemas
    "FoodCategoryCreate",
    "FoodCategoryUpdate",
    "FoodCategoryResponse",
    "InventoryItemCreate",
    "InventoryItemUpdate",
    "InventoryItemResponse",
    # Recipe schemas
    "RecipeCreate",
    "RecipeUpdate",
    "RecipeResponse",
    "RecipeFullResponse",
    "RecipeIngredientCreate",
    "RecipeIngredientResponse",
    "RecipeInstructionCreate",
    "RecipeInstructionResponse",
    "UserRecipeCreate",
    "UserRecipeUpdate",
    "UserRecipeResponse",
    # Meal plan schemas
    "MealPlanCreate",
    "MealPlanUpdate",
    "MealPlanResponse",
    "MealPlanFullResponse",
    "MealPlanItemCreate",
    "MealPlanItemUpdate",
    "MealPlanItemResponse",
    # Grocery schemas
    "GroceryListCreate",
    "GroceryListUpdate",
    "GroceryListResponse",
    "GroceryListFullResponse",
    "GroceryListItemCreate",
    "GroceryListItemUpdate",
    "GroceryListItemResponse",
    # Activity schemas
    "ActivityLogCreate",
    "ActivityLogResponse",
]
