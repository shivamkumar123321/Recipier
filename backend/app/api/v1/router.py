"""
Main API router that aggregates all v1 endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1 import auth, grocery_lists, inventory, meal_plans, recipes

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    inventory.router,
    prefix="/inventory",
    tags=["Inventory"]
)

api_router.include_router(
    recipes.router,
    prefix="/recipes",
    tags=["Recipes"]
)

api_router.include_router(
    meal_plans.router,
    prefix="/meal-plans",
    tags=["Meal Plans"]
)

api_router.include_router(
    grocery_lists.router,
    prefix="/grocery-lists",
    tags=["Grocery Lists"]
)
