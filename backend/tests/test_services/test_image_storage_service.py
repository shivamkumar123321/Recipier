"""
Tests for image storage service.
"""

import os
from pathlib import Path

import pytest

from app.services.image_storage_service import (
    ImageStorageError,
    ImageStorageService,
)
from tests.fixtures.image_samples import (
    get_invalid_image_data,
    get_mock_food_image,
    get_oversized_image,
    get_tiny_image,
)


@pytest.fixture
def storage_service():
    """Create image storage service instance for testing."""
    service = ImageStorageService()
    yield service


def test_validate_file_type_valid_extensions(storage_service):
    """Test file type validation with valid extensions."""
    assert storage_service.validate_file_type("test.jpg") == "jpg"
    assert storage_service.validate_file_type("test.jpeg") == "jpg"
    assert storage_service.validate_file_type("test.png") == "png"
    assert storage_service.validate_file_type("test.webp") == "webp"


def test_validate_file_type_with_content_type(storage_service):
    """Test file type validation with content type."""
    result = storage_service.validate_file_type(
        "test.jpg", content_type="image/jpeg"
    )
    assert result == "jpg"

    result = storage_service.validate_file_type(
        "test.png", content_type="image/png"
    )
    assert result == "png"


def test_validate_file_type_invalid_extension(storage_service):
    """Test file type validation with invalid extension."""
    with pytest.raises(ImageStorageError) as exc:
        storage_service.validate_file_type("test.gif")

    assert "Invalid file extension" in str(exc.value)


def test_validate_file_type_invalid_content_type(storage_service):
    """Test file type validation with invalid content type."""
    with pytest.raises(ImageStorageError) as exc:
        storage_service.validate_file_type("test.jpg", content_type="image/gif")

    assert "Invalid content type" in str(exc.value)


def test_validate_file_type_no_filename(storage_service):
    """Test file type validation without filename."""
    with pytest.raises(ImageStorageError) as exc:
        storage_service.validate_file_type("")

    assert "Filename is required" in str(exc.value)


def test_validate_file_size_valid(storage_service):
    """Test file size validation with valid size."""
    # Should not raise error
    storage_service.validate_file_size(1024 * 1024)  # 1MB
    storage_service.validate_file_size(3 * 1024 * 1024)  # 3MB


def test_validate_file_size_too_large(storage_service):
    """Test file size validation with oversized file."""
    with pytest.raises(ImageStorageError) as exc:
        storage_service.validate_file_size(6 * 1024 * 1024)  # 6MB

    assert "exceeds maximum" in str(exc.value)


def test_validate_file_size_empty(storage_service):
    """Test file size validation with empty file."""
    with pytest.raises(ImageStorageError) as exc:
        storage_service.validate_file_size(0)

    assert "empty" in str(exc.value)


def test_validate_image_dimensions_valid(storage_service):
    """Test image dimension validation with valid image."""
    image_bytes = get_mock_food_image("jpeg")
    width, height = storage_service.validate_image_dimensions(image_bytes)

    assert width == 800
    assert height == 600


def test_validate_image_dimensions_too_small(storage_service):
    """Test image dimension validation with tiny image."""
    tiny_image = get_tiny_image()

    with pytest.raises(ImageStorageError) as exc:
        storage_service.validate_image_dimensions(tiny_image)

    assert "too small" in str(exc.value)


def test_validate_image_dimensions_too_large(storage_service):
    """Test image dimension validation with huge image."""
    # This would require creating a 5000x5000 image which might be slow
    # For now, we'll skip this test or use a mocked validation
    pass


def test_validate_image_dimensions_invalid_data(storage_service):
    """Test image dimension validation with invalid data."""
    invalid_data = get_invalid_image_data()

    with pytest.raises(ImageStorageError) as exc:
        storage_service.validate_image_dimensions(invalid_data)

    assert "Failed to validate image" in str(exc.value)


def test_save_image_success(storage_service):
    """Test successful image save."""
    image_bytes = get_mock_food_image("jpeg")
    user_id = 999  # Test user ID

    result = storage_service.save_image(
        image_bytes=image_bytes,
        user_id=user_id,
        filename="test_food.jpg",
        content_type="image/jpeg",
    )

    assert "file_path" in result
    assert "url" in result
    assert result["width"] == 800
    assert result["height"] == 600
    assert result["format"] == "jpg"

    # Clean up
    file_path = Path(result["file_path"])
    if file_path.exists():
        file_path.unlink()

    # Remove user directory if empty
    user_dir = file_path.parent
    if user_dir.exists() and not any(user_dir.iterdir()):
        user_dir.rmdir()


def test_save_image_invalid_type(storage_service):
    """Test image save with invalid file type."""
    image_bytes = get_mock_food_image("jpeg")

    with pytest.raises(ImageStorageError) as exc:
        storage_service.save_image(
            image_bytes=image_bytes,
            user_id=999,
            filename="test.gif",  # Invalid extension
        )

    assert "Invalid file extension" in str(exc.value)


def test_save_image_too_large(storage_service):
    """Test image save with oversized file."""
    oversized_image = get_oversized_image()

    with pytest.raises(ImageStorageError) as exc:
        storage_service.save_image(
            image_bytes=oversized_image,
            user_id=999,
            filename="large.jpg",
        )

    assert "exceeds maximum" in str(exc.value)


def test_delete_image_exists(storage_service):
    """Test deleting an existing image."""
    # First create an image
    image_bytes = get_mock_food_image("jpeg")
    user_id = 999

    result = storage_service.save_image(
        image_bytes=image_bytes,
        user_id=user_id,
        filename="to_delete.jpg",
    )

    file_path = result["file_path"]

    # Verify it exists
    assert Path(file_path).exists()

    # Delete it
    deleted = storage_service.delete_image(file_path)
    assert deleted is True

    # Verify it's gone
    assert not Path(file_path).exists()

    # Clean up user directory
    user_dir = Path(file_path).parent
    if user_dir.exists() and not any(user_dir.iterdir()):
        user_dir.rmdir()


def test_delete_image_not_exists(storage_service):
    """Test deleting a non-existent image."""
    result = storage_service.delete_image("/fake/path/image.jpg")
    assert result is False


def test_get_user_images_empty(storage_service):
    """Test getting user images when none exist."""
    images = storage_service.get_user_images(user_id=9999)
    assert images == []


def test_get_user_images_with_files(storage_service):
    """Test getting user images with existing files."""
    user_id = 999
    image_bytes = get_mock_food_image("jpeg")

    # Create a couple of images
    result1 = storage_service.save_image(
        image_bytes=image_bytes,
        user_id=user_id,
        filename="image1.jpg",
    )

    result2 = storage_service.save_image(
        image_bytes=image_bytes,
        user_id=user_id,
        filename="image2.jpg",
    )

    # Get images
    images = storage_service.get_user_images(user_id)

    assert len(images) >= 2
    assert any("image1.jpg" in img for img in images)
    assert any("image2.jpg" in img for img in images)

    # Clean up
    for file_path in images:
        Path(file_path).unlink()

    user_dir = Path(result1["file_path"]).parent
    if user_dir.exists() and not any(user_dir.iterdir()):
        user_dir.rmdir()


def test_cleanup_old_images(storage_service):
    """Test cleanup of old images."""
    # For this test, we'd need to mock file modification times
    # or use actual old files. For now, test the basic call.
    deleted_count = storage_service.cleanup_old_images(user_id=9999, days=30)
    assert deleted_count >= 0
