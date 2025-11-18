"""
Comprehensive tests for inventory management endpoints.

Tests:
- Manual item creation
- Item listing with filters and pagination
- Item updates
- Item deletion
- Expiring items
- Category grouping
- Voice add (mocked)
- Image scan (mocked)
"""

from datetime import date, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import FoodCategory, InventoryItem
from app.repositories.inventory_repository import (
    food_category_repository,
    inventory_repository,
)


class TestInventoryItemCreation:
    """Test manual inventory item creation."""

    @pytest.mark.asyncio
    async def test_create_item_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test successful item creation."""
        response = await client.post(
            "/api/v1/inventory/items",
            json={
                "name": "Chicken Breast",
                "quantity": 2.5,
                "unit": "kg",
                "storage_location": "fridge",
                "expiration_date": str(date.today() + timedelta(days=7)),
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Chicken Breast"
        assert data["quantity"] == 2.5
        assert data["unit"] == "kg"
        assert data["storage_location"] == "fridge"

    @pytest.mark.asyncio
    async def test_create_item_past_expiration(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creation with past expiration date fails."""
        response = await client.post(
            "/api/v1/inventory/items",
            json={
                "name": "Milk",
                "quantity": 1,
                "unit": "L",
                "expiration_date": str(date.today() - timedelta(days=1)),
            },
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_item_invalid_storage(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creation with invalid storage location fails."""
        response = await client.post(
            "/api/v1/inventory/items",
            json={
                "name": "Bread",
                "quantity": 1,
                "unit": "loaf",
                "storage_location": "invalid_location",
            },
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_item_zero_quantity(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creation with zero quantity fails."""
        response = await client.post(
            "/api/v1/inventory/items",
            json={
                "name": "Eggs",
                "quantity": 0,
                "unit": "dozen",
            },
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error


class TestInventoryItemListing:
    """Test inventory item listing with filters."""

    @pytest.mark.asyncio
    async def test_list_items_empty(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test listing with no items."""
        response = await client.get(
            "/api/v1/inventory/items",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_items_with_data(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user
    ):
        """Test listing with items."""
        # Create test items
        item1 = await inventory_repository.create(
            db,
            {
                "user_id": test_user.id,
                "name": "Apples",
                "quantity": 5,
                "unit": "pieces",
                "storage_location": "fridge",
            },
        )
        item2 = await inventory_repository.create(
            db,
            {
                "user_id": test_user.id,
                "name": "Pasta",
                "quantity": 2,
                "unit": "kg",
                "storage_location": "pantry",
            },
        )
        await db.commit()

        response = await client.get(
            "/api/v1/inventory/items",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    @pytest.mark.asyncio
    async def test_list_items_with_storage_filter(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user
    ):
        """Test filtering by storage location."""
        # Create items in different locations
        await inventory_repository.create(
            db,
            {
                "user_id": test_user.id,
                "name": "Milk",
                "quantity": 1,
                "unit": "L",
                "storage_location": "fridge",
            },
        )
        await inventory_repository.create(
            db,
            {
                "user_id": test_user.id,
                "name": "Rice",
                "quantity": 5,
                "unit": "kg",
                "storage_location": "pantry",
            },
        )
        await db.commit()

        response = await client.get(
            "/api/v1/inventory/items?storage_location=fridge",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["storage_location"] == "fridge"

    @pytest.mark.asyncio
    async def test_list_items_with_search(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user
    ):
        """Test searching by name."""
        await inventory_repository.create(
            db,
            {
                "user_id": test_user.id,
                "name": "Green Apple",
                "quantity": 3,
                "unit": "pieces",
            },
        )
        await inventory_repository.create(
            db,
            {
                "user_id": test_user.id,
                "name": "Red Apple",
                "quantity": 2,
                "unit": "pieces",
            },
        )
        await inventory_repository.create(
            db,
            {
                "user_id": test_user.id,
                "name": "Orange",
                "quantity": 5,
                "unit": "pieces",
            },
        )
        await db.commit()

        response = await client.get(
            "/api/v1/inventory/items?search=apple",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        for item in data["items"]:
            assert "apple" in item["name"].lower()

    @pytest.mark.asyncio
    async def test_list_items_pagination(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user
    ):
        """Test pagination."""
        # Create 5 items
        for i in range(5):
            await inventory_repository.create(
                db,
                {
                    "user_id": test_user.id,
                    "name": f"Item {i}",
                    "quantity": 1,
                    "unit": "piece",
                },
            )
        await db.commit()

        # Get first page
        response = await client.get(
            "/api/v1/inventory/items?skip=0&limit=2",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["skip"] == 0
        assert data["limit"] == 2

        # Get second page
        response = await client.get(
            "/api/v1/inventory/items?skip=2&limit=2",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["skip"] == 2


class TestInventoryItemOperations:
    """Test item update and delete operations."""

    @pytest.mark.asyncio
    async def test_get_item_by_id(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user
    ):
        """Test getting single item."""
        item = await inventory_repository.create(
            db,
            {
                "user_id": test_user.id,
                "name": "Tomatoes",
                "quantity": 1.5,
                "unit": "kg",
            },
        )
        await db.commit()

        response = await client.get(
            f"/api/v1/inventory/items/{item.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item.id
        assert data["name"] == "Tomatoes"

    @pytest.mark.asyncio
    async def test_get_nonexistent_item(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting nonexistent item fails."""
        response = await client.get(
            "/api/v1/inventory/items/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_item(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user
    ):
        """Test updating item."""
        item = await inventory_repository.create(
            db,
            {
                "user_id": test_user.id,
                "name": "Cheese",
                "quantity": 200,
                "unit": "g",
            },
        )
        await db.commit()

        response = await client.patch(
            f"/api/v1/inventory/items/{item.id}",
            json={"quantity": 150},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 150
        assert data["unit"] == "g"  # Unchanged

    @pytest.mark.asyncio
    async def test_delete_item(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user
    ):
        """Test deleting item."""
        item = await inventory_repository.create(
            db,
            {
                "user_id": test_user.id,
                "name": "Old Bread",
                "quantity": 1,
                "unit": "loaf",
            },
        )
        await db.commit()

        response = await client.delete(
            f"/api/v1/inventory/items/{item.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify deleted
        get_response = await client.get(
            f"/api/v1/inventory/items/{item.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404


class TestExpiringItems:
    """Test expiring items functionality."""

    @pytest.mark.asyncio
    async def test_get_expiring_items(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user
    ):
        """Test getting items expiring soon."""
        # Create expiring item (3 days from now)
        await inventory_repository.create(
            db,
            {
                "user_id": test_user.id,
                "name": "Yogurt",
                "quantity": 1,
                "unit": "cup",
                "expiration_date": date.today() + timedelta(days=3),
            },
        )

        # Create non-expiring item (30 days from now)
        await inventory_repository.create(
            db,
            {
                "user_id": test_user.id,
                "name": "Canned Beans",
                "quantity": 1,
                "unit": "can",
                "expiration_date": date.today() + timedelta(days=30),
            },
        )

        await db.commit()

        response = await client.get(
            "/api/v1/inventory/expiring?days=7",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Yogurt"

    @pytest.mark.asyncio
    async def test_expiring_excludes_past(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user
    ):
        """Test that already expired items are excluded."""
        # Create expired item (shouldn't show up)
        await inventory_repository.create(
            db,
            {
                "user_id": test_user.id,
                "name": "Expired Milk",
                "quantity": 1,
                "unit": "L",
                "expiration_date": date.today() - timedelta(days=1),
            },
        )

        await db.commit()

        response = await client.get(
            "/api/v1/inventory/expiring?days=7",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0


class TestCategoryGrouping:
    """Test category grouping functionality."""

    @pytest.mark.asyncio
    async def test_get_items_by_category(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user
    ):
        """Test getting items grouped by category."""
        # Create category
        category = await food_category_repository.create(
            db,
            {
                "name": "Dairy",
                "description": "Dairy products",
            },
        )

        # Create items with category
        await inventory_repository.create(
            db,
            {
                "user_id": test_user.id,
                "name": "Milk",
                "quantity": 1,
                "unit": "L",
                "category_id": category.id,
            },
        )
        await inventory_repository.create(
            db,
            {
                "user_id": test_user.id,
                "name": "Cheese",
                "quantity": 200,
                "unit": "g",
                "category_id": category.id,
            },
        )

        # Create item without category
        await inventory_repository.create(
            db,
            {
                "user_id": test_user.id,
                "name": "Unknown Item",
                "quantity": 1,
                "unit": "piece",
            },
        )

        await db.commit()

        response = await client.get(
            "/api/v1/inventory/categories",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # One category + uncategorized

        # Find dairy category
        dairy_summary = next((s for s in data if s["category_name"] == "Dairy"), None)
        assert dairy_summary is not None
        assert dairy_summary["item_count"] == 2


class TestVoiceAndImageFeatures:
    """Test voice add and image scan features (mocked)."""

    @pytest.mark.asyncio
    async def test_voice_add_mocked(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test voice add endpoint with mocked OpenAI."""
        with patch("app.services.openai_service.openai_service.transcribe_audio") as mock_transcribe:
            with patch("app.services.openai_service.openai_service.parse_inventory_from_text") as mock_parse:
                # Mock responses
                mock_transcribe.return_value = "I bought 2 kilograms of chicken and 1 liter of milk"
                mock_parse.return_value = [
                    {
                        "name": "Chicken",
                        "quantity": 2.0,
                        "unit": "kg",
                        "storage_location": "fridge",
                    },
                    {
                        "name": "Milk",
                        "quantity": 1.0,
                        "unit": "L",
                        "storage_location": "fridge",
                    },
                ]

                response = await client.post(
                    "/api/v1/inventory/voice-add",
                    json={
                        "audio_data": "fake_base64_audio_data",
                        "audio_format": "webm",
                    },
                    headers=auth_headers,
                )

                assert response.status_code == 201
                data = response.json()
                assert "transcription" in data
                assert len(data["items_added"]) == 2

    @pytest.mark.asyncio
    async def test_image_scan_mocked(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test image scan endpoint with mocked OpenAI."""
        with patch("app.services.openai_service.openai_service.analyze_food_image") as mock_analyze:
            # Mock response
            mock_analyze.return_value = {
                "description": "Fresh produce on a kitchen counter",
                "items": [
                    {
                        "name": "Tomatoes",
                        "quantity": 4.0,
                        "unit": "pieces",
                        "storage_location": "fridge",
                        "estimated_shelf_life_days": 5,
                    },
                ],
            }

            response = await client.post(
                "/api/v1/inventory/scan",
                json={
                    "image_data": "fake_base64_image_data",
                    "image_format": "jpeg",
                },
                headers=auth_headers,
            )

            assert response.status_code == 201
            data = response.json()
            assert "description" in data
            assert len(data["items_added"]) == 1
            assert data["items_added"][0]["name"] == "Tomatoes"
