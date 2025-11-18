"""
Image test fixtures for vision/food recognition testing.

Provides mock image data and sample vision responses for testing.
"""

import base64
from io import BytesIO

from PIL import Image


def create_test_image(width: int = 800, height: int = 600, format: str = "JPEG") -> bytes:
    """
    Create a simple test image.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        format: Image format (JPEG, PNG, WEBP)

    Returns:
        Image bytes
    """
    # Create a simple colored image
    img = Image.new("RGB", (width, height), color=(73, 109, 137))

    # Add some simple shapes to make it look like food
    # (In real scenario, this would be an actual food photo)
    from PIL import ImageDraw

    draw = ImageDraw.Draw(img)

    # Draw some circles (representing fruits/food items)
    draw.ellipse([100, 100, 250, 250], fill=(255, 0, 0))  # Red circle (apple)
    draw.ellipse([300, 150, 400, 250], fill=(255, 0, 0))  # Another red circle
    draw.ellipse([500, 200, 650, 350], fill=(255, 255, 0))  # Yellow circle (banana)

    # Convert to bytes
    buffer = BytesIO()
    img.save(buffer, format=format)
    return buffer.getvalue()


def get_mock_food_image(format: str = "jpeg") -> bytes:
    """
    Get mock food image bytes for testing.

    Args:
        format: Image format (jpeg, png, webp)

    Returns:
        Image bytes
    """
    img_format = format.upper()
    if img_format == "JPG":
        img_format = "JPEG"

    return create_test_image(800, 600, img_format)


def get_mock_food_image_base64(format: str = "jpeg") -> str:
    """
    Get base64 encoded mock food image.

    Args:
        format: Image format

    Returns:
        Base64 encoded image string
    """
    image_bytes = get_mock_food_image(format)
    return base64.b64encode(image_bytes).decode("utf-8")


def get_invalid_image_data() -> bytes:
    """Get invalid image data (not a real image)."""
    return b"This is not an image file"


def get_oversized_image() -> bytes:
    """Get an oversized image (> 5MB) for testing size limits."""
    # Create a large image
    return create_test_image(4000, 4000, "JPEG")


def get_tiny_image() -> bytes:
    """Get a tiny image (below minimum dimensions) for testing."""
    return create_test_image(50, 50, "JPEG")


# Sample vision API responses for mocking
SAMPLE_VISION_RESPONSE_APPLES_AND_MILK = {
    "description": "The image shows 3 red apples and 1 gallon of whole milk on a kitchen counter.",
    "items": [
        {
            "name": "Red Apple",
            "confidence": 0.95,
            "quantity": 3,
            "unit": "items",
            "category": "fruit",
            "estimated_shelf_life_days": 14,
            "storage_location": "fridge",
        },
        {
            "name": "Whole Milk (1 gallon)",
            "confidence": 0.92,
            "quantity": 1,
            "unit": "gallon",
            "category": "dairy",
            "estimated_shelf_life_days": 7,
            "storage_location": "fridge",
        },
    ],
    "image_quality": "good",
}

SAMPLE_VISION_RESPONSE_VEGETABLES = {
    "description": "The image contains fresh vegetables including broccoli, carrots, and tomatoes.",
    "items": [
        {
            "name": "Broccoli",
            "confidence": 0.90,
            "quantity": 1,
            "unit": "bunch",
            "category": "vegetable",
            "estimated_shelf_life_days": 7,
            "storage_location": "fridge",
        },
        {
            "name": "Carrots",
            "confidence": 0.88,
            "quantity": 5,
            "unit": "items",
            "category": "vegetable",
            "estimated_shelf_life_days": 21,
            "storage_location": "fridge",
        },
        {
            "name": "Tomatoes",
            "confidence": 0.93,
            "quantity": 4,
            "unit": "items",
            "category": "vegetable",
            "estimated_shelf_life_days": 7,
            "storage_location": "pantry",
        },
    ],
    "image_quality": "good",
}

SAMPLE_VISION_RESPONSE_EMPTY = {
    "description": "The image does not contain any recognizable food items.",
    "items": [],
    "image_quality": "fair",
}

SAMPLE_VISION_RESPONSE_WITH_NUTRITION = {
    "description": "Grilled chicken breast with rice and steamed broccoli.",
    "items": [
        {
            "name": "Grilled Chicken Breast",
            "confidence": 0.94,
            "quantity": 1,
            "unit": "serving",
            "category": "protein",
            "estimated_shelf_life_days": 3,
            "storage_location": "fridge",
        },
        {
            "name": "White Rice",
            "confidence": 0.91,
            "quantity": 1,
            "unit": "cup",
            "category": "grain",
            "estimated_shelf_life_days": 5,
            "storage_location": "fridge",
        },
        {
            "name": "Steamed Broccoli",
            "confidence": 0.89,
            "quantity": 1,
            "unit": "cup",
            "category": "vegetable",
            "estimated_shelf_life_days": 3,
            "storage_location": "fridge",
        },
    ],
    "image_quality": "good",
    "nutrition": {
        "total_calories": 450,
        "total_protein_g": 35,
        "total_carbs_g": 50,
        "total_fat_g": 8,
        "total_fiber_g": 5,
        "items": [
            {
                "name": "Grilled Chicken Breast",
                "calories": 165,
                "protein_g": 31,
                "carbs_g": 0,
                "fat_g": 3.6,
            },
            {
                "name": "White Rice",
                "calories": 205,
                "protein_g": 4,
                "carbs_g": 45,
                "fat_g": 0.4,
            },
            {
                "name": "Steamed Broccoli",
                "calories": 80,
                "protein_g": 0,
                "carbs_g": 5,
                "fat_g": 4,
            },
        ],
    },
}

# Portion estimation responses
SAMPLE_PORTION_ESTIMATE_CHICKEN = {
    "estimated_quantity": 6,
    "unit": "oz",
    "confidence": 0.85,
}

SAMPLE_PORTION_ESTIMATE_PASTA = {
    "estimated_quantity": 1.5,
    "unit": "cups",
    "confidence": 0.78,
}
