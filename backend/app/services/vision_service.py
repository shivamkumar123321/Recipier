"""
Vision service for food image recognition with prompt engineering.

Uses OpenAI GPT-4 Vision to:
- Identify food items in images
- Estimate quantities
- Suggest storage locations and expiration dates
- Extract nutritional information
"""

import base64
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.services.openai_service import OpenAIService, OpenAIServiceError

logger = get_logger(__name__)


class VisionService:
    """
    Service for food image recognition with GPT-4 Vision.

    Uses carefully engineered prompts to:
    - Identify multiple food items in a single image
    - Estimate quantities when visible
    - Suggest appropriate storage locations
    - Estimate shelf life for meal planning
    """

    # System prompt for food identification
    FOOD_IDENTIFICATION_PROMPT = """You are an expert food recognition AI assistant. Analyze the image and identify all food items visible.

For each food item, provide:
1. **name**: Specific name of the food (e.g., "Red Apple", "Chicken Breast", "Whole Milk")
2. **confidence**: Confidence score 0.0-1.0 (how certain you are)
3. **quantity**: Estimated quantity if determinable from image (e.g., 3, 2.5, 1)
4. **unit**: Appropriate unit (items, lbs, oz, kg, bunch, bag, etc.)
5. **category**: Food category (fruit, vegetable, protein, dairy, grain, snack, beverage, prepared, condiment)
6. **estimated_shelf_life_days**: Typical shelf life in days for this food type
7. **storage_location**: Recommended storage (pantry, fridge, freezer)

Guidelines:
- If you can count items (e.g., 3 apples), provide exact quantity
- If items are packaged, estimate based on typical package sizes
- If quantity is unclear, use 1 as default
- For fresh produce, estimate shelf life based on food type
- For packaged goods, note if expiration date is visible
- Be specific with names (e.g., "Granny Smith Apple" not just "Apple" if recognizable)

Example output for image with apples and milk:
```json
{
  "description": "The image shows 3 red apples and 1 gallon of whole milk.",
  "items": [
    {
      "name": "Red Apple",
      "confidence": 0.95,
      "quantity": 3,
      "unit": "items",
      "category": "fruit",
      "estimated_shelf_life_days": 14,
      "storage_location": "fridge"
    },
    {
      "name": "Whole Milk (1 gallon)",
      "confidence": 0.90,
      "quantity": 1,
      "unit": "gallon",
      "category": "dairy",
      "estimated_shelf_life_days": 7,
      "storage_location": "fridge"
    }
  ],
  "image_quality": "good"
}
```

Respond ONLY with valid JSON matching this format. No markdown, no explanation."""

    NUTRITION_EXTRACTION_PROMPT = """You are a nutrition analysis AI. Analyze the food items and provide nutritional information.

For the identified food items, estimate total nutritional content:
- total_calories: Total estimated calories
- total_protein_g: Total protein in grams
- total_carbs_g: Total carbohydrates in grams
- total_fat_g: Total fat in grams
- total_fiber_g: Total fiber in grams
- items: Per-item breakdown with {name, calories, protein_g, carbs_g, fat_g}

Base estimates on:
- Standard USDA food database values
- Visible portions/quantities
- Typical serving sizes

Respond ONLY with valid JSON. No markdown."""

    def __init__(self, openai_service: OpenAIService):
        """
        Initialize vision service.

        Args:
            openai_service: OpenAI service instance
        """
        self.openai_service = openai_service

    async def identify_food_items(
        self,
        image_data: str,
        image_format: str = "jpeg",
        include_nutrition: bool = False,
    ) -> Dict[str, Any]:
        """
        Identify food items in an image with detailed analysis.

        Args:
            image_data: Base64 encoded image or raw bytes
            image_format: Image format (jpeg, png, webp)
            include_nutrition: Whether to include nutrition information

        Returns:
            Dictionary with:
            - description: AI description of image
            - items: List of identified food items with details
            - total_items_count: Number of items found
            - image_quality: Assessment of image quality
            - nutrition: (optional) Nutritional information

        Raises:
            OpenAIServiceError: If vision analysis fails
        """
        logger.info(
            f"Identifying food items in image (format: {image_format}, "
            f"include_nutrition: {include_nutrition})"
        )

        try:
            # Prepare image data URL
            if not image_data.startswith("data:image"):
                # Add data URL prefix if not present
                mime_type = f"image/{image_format}"
                if image_format == "jpg":
                    mime_type = "image/jpeg"

                image_url = f"data:{mime_type};base64,{image_data}"
            else:
                image_url = image_data

            # Call Vision API for food identification
            response = await self.openai_service.client.chat.completions.create(
                model=settings.OPENAI_VISION_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": self.FOOD_IDENTIFICATION_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Identify all food items in this image with quantities, storage recommendations, and shelf life estimates.",
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url},
                            },
                        ],
                    },
                ],
                max_tokens=1000,
                temperature=0.3,
            )

            # Parse response
            content = response.choices[0].message.content
            result = self.openai_service._parse_json_response(content)

            # Ensure required fields
            if "description" not in result:
                result["description"] = "Food items identified in image"

            if "items" not in result:
                result["items"] = []

            result["total_items_count"] = len(result.get("items", []))

            # Get nutrition info if requested
            if include_nutrition and result["items"]:
                nutrition = await self._extract_nutrition_info(result["items"])
                result["nutrition"] = nutrition

            logger.info(
                f"Identified {result['total_items_count']} food items "
                f"with confidence scores"
            )

            # Track usage
            if hasattr(response, "usage"):
                self.openai_service._track_usage(response.usage)

            return result

        except Exception as e:
            logger.error(f"Food identification failed: {e}")
            raise OpenAIServiceError(f"Failed to identify food items: {e}")

    async def _extract_nutrition_info(
        self, identified_items: List[Dict]
    ) -> Dict[str, Any]:
        """
        Extract nutritional information for identified food items.

        Args:
            identified_items: List of identified food items

        Returns:
            Nutrition information dictionary
        """
        try:
            # Create prompt with identified items
            items_text = "\n".join(
                [
                    f"- {item['name']} ({item.get('quantity', 1)} {item.get('unit', 'items')})"
                    for item in identified_items
                ]
            )

            response = await self.openai_service.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": self.NUTRITION_EXTRACTION_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": f"Provide nutritional information for:\n{items_text}",
                    },
                ],
                max_tokens=800,
                temperature=0.2,
            )

            content = response.choices[0].message.content
            nutrition = self.openai_service._parse_json_response(content)

            # Track usage
            if hasattr(response, "usage"):
                self.openai_service._track_usage(response.usage)

            return nutrition

        except Exception as e:
            logger.error(f"Nutrition extraction failed: {e}")
            return {
                "total_calories": None,
                "total_protein_g": None,
                "total_carbs_g": None,
                "total_fat_g": None,
                "items": [],
            }

    async def estimate_portion_size(
        self, image_data: str, food_name: str, reference_object: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Estimate portion size using reference objects in the image.

        Args:
            image_data: Base64 encoded image
            food_name: Name of food to estimate
            reference_object: Optional reference object for scale (e.g., "hand", "plate")

        Returns:
            Portion estimate with quantity and unit
        """
        prompt = f"""Estimate the portion size of {food_name} in this image."""

        if reference_object:
            prompt += f" Use the {reference_object} as a reference for scale."

        prompt += """ Provide:
        - estimated_quantity: Numeric value
        - unit: Appropriate unit (oz, cup, serving, etc.)
        - confidence: Confidence 0.0-1.0

        Respond with JSON only."""

        try:
            image_url = f"data:image/jpeg;base64,{image_data}"

            response = await self.openai_service.client.chat.completions.create(
                model=settings.OPENAI_VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    },
                ],
                max_tokens=200,
                temperature=0.2,
            )

            content = response.choices[0].message.content
            result = self.openai_service._parse_json_response(content)

            # Track usage
            if hasattr(response, "usage"):
                self.openai_service._track_usage(response.usage)

            return result

        except Exception as e:
            logger.error(f"Portion estimation failed: {e}")
            raise OpenAIServiceError(f"Failed to estimate portion: {e}")


def get_vision_service() -> VisionService:
    """Get or create vision service instance."""
    openai_service = OpenAIService(api_key=settings.OPENAI_API_KEY)
    return VisionService(openai_service)
