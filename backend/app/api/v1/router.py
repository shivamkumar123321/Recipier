"""
Main API router that aggregates all v1 endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    grocery_lists,
    inventory,
    meal_plans,
    notifications,
    recipes,
    vision,
    voice,
    websocket,
)

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

api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"]
)

api_router.include_router(
    voice.router,
    prefix="/voice",
    tags=["Voice"]
)

api_router.include_router(
    vision.router,
    prefix="/vision",
    tags=["Vision"]
)

# Include WebSocket router (no prefix)
api_router.include_router(
    websocket.router,
    tags=["WebSocket"]
)
