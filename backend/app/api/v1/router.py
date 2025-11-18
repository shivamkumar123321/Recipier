"""
Main API router that aggregates all v1 endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1 import auth, inventory

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

# Note: Add more routers as you implement them
# api_router.include_router(
#     meals.router,
#     prefix="/meals",
#     tags=["Meals"]
# )
