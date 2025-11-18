"""
Tests for meal plan API endpoints.
"""

from datetime import date, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recipe import Recipe
from app.models.user import User
from app.repositories.inventory_repository import inventory_repository
from app.repositories.meal_plan_repository import (
    meal_plan_item_repository,
    meal_plan_repository,
)
from app.repositories.recipe_repository import (
    recipe_ingredient_repository,
    recipe_repository,
)


@pytest.mark.asyncio
async def test_get_meal_plans_empty(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test getting meal plans when none exist."""
    response = await client.get(
        "/api/v1/meal-plans/",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_get_meal_plans_with_status_filter(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test getting meal plans with status filter."""
    # Create active and completed meal plans
    today = date.today()

    await meal_plan_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Active Plan",
            "start_date": today,
            "end_date": today + timedelta(days=7),
            "status": "active",
        },
    )

    await meal_plan_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Completed Plan",
            "start_date": today - timedelta(days=14),
            "end_date": today - timedelta(days=7),
            "status": "completed",
        },
    )

    await db.commit()

    # Get active meal plans
    response = await client.get(
        "/api/v1/meal-plans/?status=active",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Active Plan"

    # Get completed meal plans
    response = await client.get(
        "/api/v1/meal-plans/?status=completed",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Completed Plan"


@pytest.mark.asyncio
async def test_generate_ai_meal_plan(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
):
    """Test AI meal plan generation (placeholder)."""
    today = date.today()
    end_date = today + timedelta(days=7)

    response = await client.post(
        "/api/v1/meal-plans/generate",
        headers=verified_auth_headers,
        json={
            "name": "Weekly Meal Plan",
            "start_date": today.isoformat(),
            "end_date": end_date.isoformat(),
            "target_calories": 2000,
            "macro_targets": {
                "protein_g": 150,
                "carbs_g": 200,
                "fat_g": 70,
            },
            "dietary_preferences": ["vegetarian"],
            "excluded_ingredients": ["peanuts"],
            "meal_types": ["breakfast", "lunch", "dinner"],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert "meal_plan" in data
    assert data["meal_plan"]["name"] == "Weekly Meal Plan"
    assert data["meal_plan"]["target_calories"] == 2000
    assert "PLACEHOLDER" in data["message"]

    # Should have created meal plan items (3 meals per day for 7 days = 21 meals)
    meal_plan_items = data["meal_plan"]["meal_plan_items"]
    assert len(meal_plan_items) >= 21


@pytest.mark.asyncio
async def test_generate_ai_meal_plan_invalid_dates(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test AI meal plan generation with invalid dates."""
    today = date.today()

    response = await client.post(
        "/api/v1/meal-plans/generate",
        headers=verified_auth_headers,
        json={
            "name": "Invalid Plan",
            "start_date": today.isoformat(),
            "end_date": (today - timedelta(days=1)).isoformat(),  # End before start
            "meal_types": ["breakfast"],
        },
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_meal_plan_by_id(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test getting a specific meal plan with items."""
    today = date.today()

    # Create meal plan
    meal_plan = await meal_plan_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Test Plan",
            "start_date": today,
            "end_date": today + timedelta(days=3),
            "status": "active",
        },
    )

    # Add meal plan items
    await meal_plan_item_repository.bulk_create(
        db,
        meal_plan.id,
        [
            {
                "scheduled_date": today,
                "meal_type": "breakfast",
                "servings": 1,
            },
            {
                "scheduled_date": today,
                "meal_type": "lunch",
                "servings": 1,
            },
        ],
    )

    await db.commit()

    # Get meal plan
    response = await client.get(
        f"/api/v1/meal-plans/{meal_plan.id}",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Plan"
    assert len(data["meal_plan_items"]) == 2


@pytest.mark.asyncio
async def test_get_meal_plan_not_found(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test getting a non-existent meal plan."""
    response = await client.get(
        "/api/v1/meal-plans/999999",
        headers=verified_auth_headers,
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_meal_plan_unauthorized(
    client: AsyncClient,
    test_user: User,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test getting another user's meal plan."""
    today = date.today()

    # Create meal plan for test_user
    meal_plan = await meal_plan_repository.create(
        db,
        {
            "user_id": test_user.id,  # Different user
            "name": "Test Plan",
            "start_date": today,
            "end_date": today + timedelta(days=3),
            "status": "active",
        },
    )
    await db.commit()

    # Try to access with verified_user's token
    response = await client.get(
        f"/api/v1/meal-plans/{meal_plan.id}",
        headers=verified_auth_headers,
    )

    assert response.status_code == 404  # Not found (access denied)


@pytest.mark.asyncio
async def test_cook_meal_without_recipe(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test marking a meal as cooked (no recipe linked)."""
    today = date.today()

    # Create meal plan
    meal_plan = await meal_plan_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Test Plan",
            "start_date": today,
            "end_date": today + timedelta(days=3),
            "status": "active",
        },
    )

    # Add meal plan item (no recipe)
    items = await meal_plan_item_repository.bulk_create(
        db,
        meal_plan.id,
        [
            {
                "scheduled_date": today,
                "meal_type": "breakfast",
                "servings": 1,
                "recipe_id": None,
            }
        ],
    )

    await db.commit()

    # Cook meal
    response = await client.post(
        f"/api/v1/meal-plans/{meal_plan.id}/cook",
        headers=verified_auth_headers,
        json={"meal_plan_item_id": items[0].id},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["meal_plan_item"]["is_completed"] is True
    assert data["inventory_updated"] is False
    assert data["items_deducted"] == 0


@pytest.mark.asyncio
async def test_cook_meal_with_recipe_and_inventory_update(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test marking a meal as cooked with inventory deduction."""
    today = date.today()

    # Create recipe with ingredients
    recipe = await recipe_repository.create(
        db,
        {
            "name": "Pasta",
            "servings": 2,
            "is_public": True,
        },
    )

    await recipe_ingredient_repository.bulk_create(
        db,
        recipe.id,
        [
            {
                "ingredient_name": "Pasta",
                "quantity": 200,
                "unit": "g",
                "order_index": 0,
            },
            {
                "ingredient_name": "Tomato Sauce",
                "quantity": 1,
                "unit": "cup",
                "order_index": 1,
            },
        ],
    )

    # Add items to inventory
    await inventory_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Pasta",
            "quantity": 500,
            "unit": "g",
        },
    )

    await inventory_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Tomato Sauce",
            "quantity": 3,
            "unit": "cup",
        },
    )

    # Create meal plan
    meal_plan = await meal_plan_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Test Plan",
            "start_date": today,
            "end_date": today + timedelta(days=3),
            "status": "active",
        },
    )

    # Add meal plan item with recipe
    items = await meal_plan_item_repository.bulk_create(
        db,
        meal_plan.id,
        [
            {
                "scheduled_date": today,
                "meal_type": "lunch",
                "servings": 1,  # 1 serving (recipe is for 2)
                "recipe_id": recipe.id,
            }
        ],
    )

    await db.commit()

    # Cook meal
    response = await client.post(
        f"/api/v1/meal-plans/{meal_plan.id}/cook",
        headers=verified_auth_headers,
        json={"meal_plan_item_id": items[0].id},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["meal_plan_item"]["is_completed"] is True
    assert data["inventory_updated"] is True
    assert data["items_deducted"] == 2  # Both ingredients


@pytest.mark.asyncio
async def test_cook_meal_already_cooked(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test cooking a meal that's already marked as cooked."""
    today = date.today()

    # Create meal plan
    meal_plan = await meal_plan_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Test Plan",
            "start_date": today,
            "end_date": today + timedelta(days=3),
            "status": "active",
        },
    )

    # Add meal plan item
    items = await meal_plan_item_repository.bulk_create(
        db,
        meal_plan.id,
        [
            {
                "scheduled_date": today,
                "meal_type": "breakfast",
                "servings": 1,
                "is_completed": True,  # Already cooked
            }
        ],
    )

    await db.commit()

    # Try to cook again
    response = await client.post(
        f"/api/v1/meal-plans/{meal_plan.id}/cook",
        headers=verified_auth_headers,
        json={"meal_plan_item_id": items[0].id},
    )

    assert response.status_code == 400
    assert "already" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_meal_plan_pagination(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test meal plan pagination."""
    today = date.today()

    # Create multiple meal plans
    for i in range(5):
        await meal_plan_repository.create(
            db,
            {
                "user_id": verified_user.id,
                "name": f"Plan {i}",
                "start_date": today + timedelta(days=i * 7),
                "end_date": today + timedelta(days=i * 7 + 6),
                "status": "active",
            },
        )
    await db.commit()

    # Get first page
    response = await client.get(
        "/api/v1/meal-plans/?skip=0&limit=2",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
