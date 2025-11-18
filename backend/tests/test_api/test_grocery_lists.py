"""
Tests for grocery list API endpoints.
"""

from datetime import date, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.grocery_repository import (
    grocery_list_item_repository,
    grocery_list_repository,
)
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
async def test_get_grocery_lists_empty(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test getting grocery lists when none exist."""
    response = await client.get(
        "/api/v1/grocery-lists/",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_get_grocery_lists_with_status_filter(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test getting grocery lists with status filter."""
    # Create active and completed lists
    await grocery_list_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Active List",
            "status": "active",
        },
    )

    await grocery_list_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Completed List",
            "status": "completed",
        },
    )

    await db.commit()

    # Get active lists
    response = await client.get(
        "/api/v1/grocery-lists/?status=active",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Active List"

    # Get completed lists
    response = await client.get(
        "/api/v1/grocery-lists/?status=completed",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Completed List"


@pytest.mark.asyncio
async def test_generate_grocery_list_from_meal_plan(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test generating grocery list from a meal plan."""
    today = date.today()

    # Create recipes with ingredients
    recipe1 = await recipe_repository.create(
        db,
        {
            "name": "Pasta",
            "servings": 2,
            "is_public": True,
        },
    )

    await recipe_ingredient_repository.bulk_create(
        db,
        recipe1.id,
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

    recipe2 = await recipe_repository.create(
        db,
        {
            "name": "Salad",
            "servings": 1,
            "is_public": True,
        },
    )

    await recipe_ingredient_repository.bulk_create(
        db,
        recipe2.id,
        [
            {
                "ingredient_name": "Lettuce",
                "quantity": 1,
                "unit": "head",
                "order_index": 0,
            },
            {
                "ingredient_name": "Tomato Sauce",  # Duplicate ingredient
                "quantity": 0.5,
                "unit": "cup",
                "order_index": 1,
            },
        ],
    )

    # Create meal plan
    meal_plan = await meal_plan_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Weekly Plan",
            "start_date": today,
            "end_date": today + timedelta(days=7),
            "status": "active",
        },
    )

    # Add meal plan items with recipes
    await meal_plan_item_repository.bulk_create(
        db,
        meal_plan.id,
        [
            {
                "scheduled_date": today,
                "meal_type": "lunch",
                "servings": 1,
                "recipe_id": recipe1.id,
            },
            {
                "scheduled_date": today,
                "meal_type": "dinner",
                "servings": 1,
                "recipe_id": recipe2.id,
            },
        ],
    )

    await db.commit()

    # Generate grocery list
    response = await client.post(
        "/api/v1/grocery-lists/generate",
        headers=verified_auth_headers,
        json={
            "meal_plan_id": meal_plan.id,
            "name": "My Grocery List",
            "exclude_inventory_items": False,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert "grocery_list" in data
    assert data["grocery_list"]["name"] == "My Grocery List"
    assert data["items_excluded"] == 0

    # Should have 3 items (Pasta, Lettuce, and Tomato Sauce aggregated)
    items = data["grocery_list"]["items"]
    assert len(items) == 3

    # Check that Tomato Sauce is aggregated (1 + 0.5 = 1.5)
    tomato_sauce_item = next(
        (item for item in items if item["item_name"] == "Tomato Sauce"), None
    )
    assert tomato_sauce_item is not None
    assert tomato_sauce_item["quantity"] == 1.5


@pytest.mark.asyncio
async def test_generate_grocery_list_excluding_inventory(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test generating grocery list with inventory exclusion."""
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

    # Add Pasta to inventory (sufficient quantity)
    await inventory_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Pasta",
            "quantity": 500,  # More than needed
            "unit": "g",
        },
    )

    # Create meal plan
    meal_plan = await meal_plan_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Plan",
            "start_date": today,
            "end_date": today + timedelta(days=3),
            "status": "active",
        },
    )

    await meal_plan_item_repository.bulk_create(
        db,
        meal_plan.id,
        [
            {
                "scheduled_date": today,
                "meal_type": "lunch",
                "servings": 1,
                "recipe_id": recipe.id,
            }
        ],
    )

    await db.commit()

    # Generate grocery list with inventory exclusion
    response = await client.post(
        "/api/v1/grocery-lists/generate",
        headers=verified_auth_headers,
        json={
            "meal_plan_id": meal_plan.id,
            "exclude_inventory_items": True,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["items_excluded"] == 1  # Pasta excluded

    # Should only have Tomato Sauce
    items = data["grocery_list"]["items"]
    assert len(items) == 1
    assert items[0]["item_name"] == "Tomato Sauce"


@pytest.mark.asyncio
async def test_generate_grocery_list_already_exists(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test generating grocery list when one already exists for the meal plan."""
    today = date.today()

    # Create meal plan
    meal_plan = await meal_plan_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Plan",
            "start_date": today,
            "end_date": today + timedelta(days=3),
            "status": "active",
        },
    )

    # Create grocery list for this meal plan
    await grocery_list_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "meal_plan_id": meal_plan.id,
            "name": "Existing List",
            "status": "active",
        },
    )

    await db.commit()

    # Try to generate another list
    response = await client.post(
        "/api/v1/grocery-lists/generate",
        headers=verified_auth_headers,
        json={"meal_plan_id": meal_plan.id},
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_generate_grocery_list_meal_plan_not_found(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test generating grocery list from non-existent meal plan."""
    response = await client.post(
        "/api/v1/grocery-lists/generate",
        headers=verified_auth_headers,
        json={"meal_plan_id": 999999},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_grocery_list_by_id(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test getting a specific grocery list with items."""
    # Create grocery list
    grocery_list = await grocery_list_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Test List",
            "status": "active",
        },
    )

    # Add items
    await grocery_list_item_repository.bulk_create(
        db,
        grocery_list.id,
        [
            {
                "item_name": "Milk",
                "quantity": 1,
                "unit": "liter",
                "is_checked": False,
                "order_index": 0,
            },
            {
                "item_name": "Bread",
                "quantity": 2,
                "unit": "loaves",
                "is_checked": False,
                "order_index": 1,
            },
        ],
    )

    await db.commit()

    # Get grocery list
    response = await client.get(
        f"/api/v1/grocery-lists/{grocery_list.id}",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test List"
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_get_grocery_list_not_found(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test getting a non-existent grocery list."""
    response = await client.get(
        "/api/v1/grocery-lists/999999",
        headers=verified_auth_headers,
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_check_grocery_list_item(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test checking a grocery list item."""
    # Create grocery list
    grocery_list = await grocery_list_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Test List",
            "status": "active",
        },
    )

    # Add item
    items = await grocery_list_item_repository.bulk_create(
        db,
        grocery_list.id,
        [
            {
                "item_name": "Milk",
                "quantity": 1,
                "unit": "liter",
                "is_checked": False,
                "order_index": 0,
            }
        ],
    )

    await db.commit()

    # Check item
    response = await client.patch(
        f"/api/v1/grocery-lists/{grocery_list.id}/item/{items[0].id}",
        headers=verified_auth_headers,
        json={"is_checked": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["item"]["is_checked"] is True
    assert "checked" in data["message"].lower()


@pytest.mark.asyncio
async def test_uncheck_grocery_list_item(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test unchecking a grocery list item."""
    # Create grocery list
    grocery_list = await grocery_list_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Test List",
            "status": "active",
        },
    )

    # Add checked item
    items = await grocery_list_item_repository.bulk_create(
        db,
        grocery_list.id,
        [
            {
                "item_name": "Milk",
                "quantity": 1,
                "unit": "liter",
                "is_checked": True,
                "order_index": 0,
            }
        ],
    )

    await db.commit()

    # Uncheck item
    response = await client.patch(
        f"/api/v1/grocery-lists/{grocery_list.id}/item/{items[0].id}",
        headers=verified_auth_headers,
        json={"is_checked": False},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["item"]["is_checked"] is False
    assert "unchecked" in data["message"].lower()


@pytest.mark.asyncio
async def test_check_item_not_found(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test checking a non-existent item."""
    # Create grocery list
    grocery_list = await grocery_list_repository.create(
        db,
        {
            "user_id": verified_user.id,
            "name": "Test List",
            "status": "active",
        },
    )
    await db.commit()

    # Try to check non-existent item
    response = await client.patch(
        f"/api/v1/grocery-lists/{grocery_list.id}/item/999999",
        headers=verified_auth_headers,
        json={"is_checked": True},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_grocery_list_pagination(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test grocery list pagination."""
    # Create multiple grocery lists
    for i in range(5):
        await grocery_list_repository.create(
            db,
            {
                "user_id": verified_user.id,
                "name": f"List {i}",
                "status": "active",
            },
        )
    await db.commit()

    # Get first page
    response = await client.get(
        "/api/v1/grocery-lists/?skip=0&limit=2",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
