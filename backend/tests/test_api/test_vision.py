"""
Tests for vision/food recognition API endpoints.
"""

import io
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import AsyncClient

from tests.fixtures.image_samples import (
    SAMPLE_VISION_RESPONSE_APPLES_AND_MILK,
    SAMPLE_VISION_RESPONSE_VEGETABLES,
    SAMPLE_VISION_RESPONSE_WITH_NUTRITION,
    get_invalid_image_data,
    get_mock_food_image,
    get_mock_food_image_base64,
    get_oversized_image,
    get_tiny_image,
)


@pytest.mark.asyncio
async def test_identify_food_in_image_success(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test successful food identification from base64 image."""
    with patch("app.api.v1.vision.get_vision_service") as mock_service:
        # Mock vision service
        mock_vision = Mock()
        mock_vision.identify_food_items = AsyncMock(
            return_value=SAMPLE_VISION_RESPONSE_APPLES_AND_MILK
        )
        mock_service.return_value = mock_vision

        image_base64 = get_mock_food_image_base64("jpeg")

        response = await client.post(
            "/api/v1/vision/identify",
            headers=verified_auth_headers,
            json={
                "image_data": image_base64,
                "image_format": "jpeg",
                "include_nutrition": False,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "description" in data
        assert "items" in data
        assert data["total_items_count"] == 2
        assert len(data["items"]) == 2
        assert data["items"][0]["name"] == "Red Apple"
        assert data["items"][0]["quantity"] == 3


@pytest.mark.asyncio
async def test_identify_food_with_nutrition(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test food identification with nutrition information."""
    with patch("app.api.v1.vision.get_vision_service") as mock_service:
        mock_vision = Mock()
        mock_vision.identify_food_items = AsyncMock(
            return_value=SAMPLE_VISION_RESPONSE_WITH_NUTRITION
        )
        mock_service.return_value = mock_vision

        image_base64 = get_mock_food_image_base64("jpeg")

        response = await client.post(
            "/api/v1/vision/identify",
            headers=verified_auth_headers,
            json={
                "image_data": image_base64,
                "image_format": "jpeg",
                "include_nutrition": True,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_items_count"] == 3
        assert "nutrition" in data
        assert data["nutrition"]["total_calories"] == 450
        assert data["nutrition"]["total_protein_g"] == 35


@pytest.mark.asyncio
async def test_identify_food_file_upload_success(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test food identification from uploaded file."""
    with patch("app.api.v1.vision.get_vision_service") as mock_service, \
         patch("app.api.v1.vision.image_storage_service") as mock_storage:

        # Mock vision service
        mock_vision = Mock()
        mock_vision.identify_food_items = AsyncMock(
            return_value=SAMPLE_VISION_RESPONSE_VEGETABLES
        )
        mock_service.return_value = mock_vision

        # Mock storage service
        mock_storage.validate_file_type.return_value = "jpeg"
        mock_storage.validate_file_size.return_value = None
        mock_storage.validate_image_dimensions.return_value = (800, 600)
        mock_storage.save_image.return_value = {
            "url": "/uploads/images/1/123456_test.jpg",
            "width": 800,
            "height": 600,
            "size": 50000,
            "format": "jpeg",
        }

        # Create mock image file
        image_bytes = get_mock_food_image("jpeg")
        files = {
            "image_file": ("vegetables.jpg", io.BytesIO(image_bytes), "image/jpeg")
        }
        data = {
            "include_nutrition": "false",
            "save_image": "true",
        }

        response = await client.post(
            "/api/v1/vision/identify/file",
            headers=verified_auth_headers,
            files=files,
            data=data,
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["total_items_count"] == 3
        assert "Broccoli" in [item["name"] for item in response_data["items"]]
        assert "image_url" in response_data
        assert "image_metadata" in response_data
        assert response_data["image_metadata"]["width"] == 800


@pytest.mark.asyncio
async def test_identify_food_file_invalid_type(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test food identification with invalid file type."""
    # Create a text file instead of image
    files = {
        "image_file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")
    }

    response = await client.post(
        "/api/v1/vision/identify/file",
        headers=verified_auth_headers,
        files=files,
    )

    assert response.status_code == 400
    assert "Invalid" in response.json()["detail"]


@pytest.mark.asyncio
async def test_identify_food_file_too_large(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test food identification with oversized file."""
    # Create oversized image
    large_image = get_oversized_image()
    files = {
        "image_file": ("large.jpg", io.BytesIO(large_image), "image/jpeg")
    }

    response = await client.post(
        "/api/v1/vision/identify/file",
        headers=verified_auth_headers,
        files=files,
    )

    assert response.status_code == 400
    assert "size" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_identify_food_file_too_small_dimensions(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test food identification with tiny image."""
    tiny_image = get_tiny_image()
    files = {
        "image_file": ("tiny.jpg", io.BytesIO(tiny_image), "image/jpeg")
    }

    response = await client.post(
        "/api/v1/vision/identify/file",
        headers=verified_auth_headers,
        files=files,
    )

    assert response.status_code == 400
    assert "dimensions" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_identify_food_unauthorized(
    client: AsyncClient,
):
    """Test food identification without authentication."""
    image_base64 = get_mock_food_image_base64("jpeg")

    response = await client.post(
        "/api/v1/vision/identify",
        json={
            "image_data": image_base64,
            "image_format": "jpeg",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_identify_food_vision_api_error(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test food identification with Vision API error."""
    with patch("app.api.v1.vision.get_vision_service") as mock_service:
        from app.services.openai_service import OpenAIServiceError

        mock_vision = Mock()
        mock_vision.identify_food_items = AsyncMock(
            side_effect=OpenAIServiceError("Vision API error")
        )
        mock_service.return_value = mock_vision

        image_base64 = get_mock_food_image_base64("jpeg")

        response = await client.post(
            "/api/v1/vision/identify",
            headers=verified_auth_headers,
            json={
                "image_data": image_base64,
                "image_format": "jpeg",
            },
        )

        assert response.status_code == 502
        assert "Vision service error" in response.json()["detail"]


@pytest.mark.asyncio
async def test_estimate_portion_size(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test portion size estimation."""
    with patch("app.api.v1.vision.get_vision_service") as mock_service:
        from tests.fixtures.image_samples import SAMPLE_PORTION_ESTIMATE_CHICKEN

        mock_vision = Mock()
        mock_vision.estimate_portion_size = AsyncMock(
            return_value=SAMPLE_PORTION_ESTIMATE_CHICKEN
        )
        mock_service.return_value = mock_vision

        image_bytes = get_mock_food_image("jpeg")
        files = {
            "image_file": ("chicken.jpg", io.BytesIO(image_bytes), "image/jpeg")
        }
        data = {
            "food_name": "Grilled Chicken Breast",
            "reference_object": "hand",
        }

        response = await client.post(
            "/api/v1/vision/estimate-portion",
            headers=verified_auth_headers,
            files=files,
            data=data,
        )

        assert response.status_code == 200
        result = response.json()
        assert result["estimated_quantity"] == 6
        assert result["unit"] == "oz"
        assert result["confidence"] == 0.85


# Integration tests with inventory

@pytest.mark.asyncio
async def test_inventory_scan_file_endpoint(
    client: AsyncClient,
    verified_auth_headers: dict,
    db,
):
    """Test inventory scan with file upload."""
    with patch("app.services.inventory_service.OpenAIService") as mock_openai:
        # Mock OpenAI service for inventory service
        mock_service = Mock()
        mock_service.analyze_food_image = AsyncMock(
            return_value={
                "description": "2 apples",
                "items": [{"name": "Apple", "estimated_calories": 95}],
            }
        )
        mock_openai.return_value = mock_service

        image_bytes = get_mock_food_image("jpeg")
        files = {
            "image_file": ("apples.jpg", io.BytesIO(image_bytes), "image/jpeg")
        }

        response = await client.post(
            "/api/v1/inventory/scan/file",
            headers=verified_auth_headers,
            files=files,
        )

        assert response.status_code == 201
        data = response.json()
        assert "description" in data
        assert "items_added" in data


@pytest.mark.asyncio
async def test_inventory_scan_file_invalid_image(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test inventory scan with invalid image."""
    invalid_data = get_invalid_image_data()
    files = {
        "image_file": ("notimage.jpg", io.BytesIO(invalid_data), "image/jpeg")
    }

    response = await client.post(
        "/api/v1/inventory/scan/file",
        headers=verified_auth_headers,
        files=files,
    )

    assert response.status_code == 400
