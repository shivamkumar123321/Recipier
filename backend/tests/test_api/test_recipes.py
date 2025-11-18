"""
Tests for recipe API endpoints.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recipe import Recipe, RecipeIngredient, RecipeInstruction
from app.models.user import User
from app.repositories.recipe_repository import (
    recipe_ingredient_repository,
    recipe_instruction_repository,
    recipe_repository,
)


@pytest.mark.asyncio
async def test_search_recipes_empty(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test searching recipes when none exist."""
    response = await client.get(
        "/api/v1/recipes/search",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_search_recipes_with_filters(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test searching recipes with filters."""
    # Create test recipes
    recipe1 = await recipe_repository.create(
        db,
        {
            "name": "Easy Pasta",
            "description": "Quick pasta dish",
            "servings": 2,
            "difficulty": "easy",
            "prep_time_minutes": 10,
            "cook_time_minutes": 20,
            "calories_per_serving": 400,
            "is_public": True,
        },
    )

    recipe2 = await recipe_repository.create(
        db,
        {
            "name": "Complex Stew",
            "description": "Hearty beef stew",
            "servings": 4,
            "difficulty": "hard",
            "prep_time_minutes": 30,
            "cook_time_minutes": 120,
            "calories_per_serving": 600,
            "is_public": True,
        },
    )

    await db.commit()

    # Search by difficulty
    response = await client.get(
        "/api/v1/recipes/search?difficulty=easy",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Easy Pasta"

    # Search by max calories
    response = await client.get(
        "/api/v1/recipes/search?max_calories=500",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Easy Pasta"

    # Search by name
    response = await client.get(
        "/api/v1/recipes/search?search=stew",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Complex Stew"


@pytest.mark.asyncio
async def test_get_recipe_by_id(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test getting a recipe by ID."""
    # Create test recipe with ingredients and instructions
    recipe = await recipe_repository.create(
        db,
        {
            "name": "Test Recipe",
            "description": "Test description",
            "servings": 2,
            "is_public": True,
        },
    )

    # Add ingredients
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

    # Add instructions
    await recipe_instruction_repository.bulk_create(
        db,
        recipe.id,
        [
            {
                "step_number": 1,
                "instruction": "Boil water",
            },
            {
                "step_number": 2,
                "instruction": "Cook pasta",
            },
        ],
    )

    await db.commit()

    # Get recipe
    response = await client.get(
        f"/api/v1/recipes/{recipe.id}",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Recipe"
    assert data["description"] == "Test description"

    # Views count should be incremented (initially 0, now 1)
    await db.refresh(recipe)
    assert recipe.views_count == 1


@pytest.mark.asyncio
async def test_get_recipe_not_found(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test getting a non-existent recipe."""
    response = await client.get(
        "/api/v1/recipes/999999",
        headers=verified_auth_headers,
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_save_recipe_to_favorites(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test saving a recipe to favorites."""
    # Create test recipe
    recipe = await recipe_repository.create(
        db,
        {
            "name": "Favorite Recipe",
            "servings": 2,
            "is_public": True,
        },
    )
    await db.commit()

    # Save to favorites
    response = await client.post(
        "/api/v1/recipes/favorites",
        headers=verified_auth_headers,
        json={
            "recipe_id": recipe.id,
            "notes": "Great recipe!",
            "rating": 5,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["recipe_id"] == recipe.id
    assert data["notes"] == "Great recipe!"
    assert data["rating"] == 5

    # Saves count should be incremented
    await db.refresh(recipe)
    assert recipe.saves_count == 1


@pytest.mark.asyncio
async def test_save_recipe_already_saved(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test saving a recipe that's already in favorites."""
    # Create and save recipe
    recipe = await recipe_repository.create(
        db,
        {
            "name": "Recipe",
            "servings": 2,
            "is_public": True,
        },
    )
    await db.commit()

    # Save to favorites
    await client.post(
        "/api/v1/recipes/favorites",
        headers=verified_auth_headers,
        json={"recipe_id": recipe.id},
    )

    # Try to save again
    response = await client.post(
        "/api/v1/recipes/favorites",
        headers=verified_auth_headers,
        json={"recipe_id": recipe.id},
    )

    assert response.status_code == 400
    assert "already saved" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_save_recipe_not_found(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test saving a non-existent recipe."""
    response = await client.post(
        "/api/v1/recipes/favorites",
        headers=verified_auth_headers,
        json={"recipe_id": 999999},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_remove_recipe_from_favorites(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test removing a recipe from favorites."""
    # Create and save recipe
    recipe = await recipe_repository.create(
        db,
        {
            "name": "Recipe",
            "servings": 2,
            "is_public": True,
        },
    )
    await db.commit()

    # Save to favorites
    await client.post(
        "/api/v1/recipes/favorites",
        headers=verified_auth_headers,
        json={"recipe_id": recipe.id},
    )

    # Remove from favorites
    response = await client.delete(
        f"/api/v1/recipes/favorites/{recipe.id}",
        headers=verified_auth_headers,
    )

    assert response.status_code == 204

    # Saves count should be decremented
    await db.refresh(recipe)
    assert recipe.saves_count == 0


@pytest.mark.asyncio
async def test_remove_recipe_not_in_favorites(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test removing a recipe that's not in favorites."""
    # Create recipe (but don't save it)
    recipe = await recipe_repository.create(
        db,
        {
            "name": "Recipe",
            "servings": 2,
            "is_public": True,
        },
    )
    await db.commit()

    # Try to remove from favorites
    response = await client.delete(
        f"/api/v1/recipes/favorites/{recipe.id}",
        headers=verified_auth_headers,
    )

    assert response.status_code == 404
    assert "not in favorites" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_my_favorite_recipes(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test getting user's favorite recipes."""
    # Create and save multiple recipes
    for i in range(3):
        recipe = await recipe_repository.create(
            db,
            {
                "name": f"Recipe {i}",
                "servings": 2,
                "is_public": True,
            },
        )
        await db.commit()

        await client.post(
            "/api/v1/recipes/favorites",
            headers=verified_auth_headers,
            json={"recipe_id": recipe.id},
        )

    # Get favorites
    response = await client.get(
        "/api/v1/recipes/favorites/my",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_recipe_pagination(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test recipe search pagination."""
    # Create multiple recipes
    for i in range(5):
        await recipe_repository.create(
            db,
            {
                "name": f"Recipe {i}",
                "servings": 2,
                "is_public": True,
            },
        )
    await db.commit()

    # Get first page
    response = await client.get(
        "/api/v1/recipes/search?skip=0&limit=2",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2

    # Get second page
    response = await client.get(
        "/api/v1/recipes/search?skip=2&limit=2",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_recipe_sorting(
    client: AsyncClient,
    verified_user: User,
    verified_auth_headers: dict,
    db: AsyncSession,
):
    """Test recipe search sorting."""
    # Create recipes with different names
    await recipe_repository.create(
        db,
        {
            "name": "Zebra Cake",
            "servings": 2,
            "is_public": True,
        },
    )
    await recipe_repository.create(
        db,
        {
            "name": "Apple Pie",
            "servings": 2,
            "is_public": True,
        },
    )
    await db.commit()

    # Sort by name ascending
    response = await client.get(
        "/api/v1/recipes/search?sort_by=name&sort_order=asc",
        headers=verified_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["name"] == "Apple Pie"
    assert data["items"][1]["name"] == "Zebra Cake"
