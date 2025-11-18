"""
OpenAI service for AI-powered features.

Provides:
- Speech-to-text (Whisper)
- Image recognition (GPT-4 Vision)
- Nutrition analysis (GPT-4)
- Meal recommendations
"""

import base64
import json
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIService:
    """Service for OpenAI API interactions."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE

    async def transcribe_audio(
        self,
        audio_data: bytes,
        audio_format: str = "webm",
    ) -> str:
        """
        Transcribe audio to text using Whisper.

        Args:
            audio_data: Audio file bytes
            audio_format: Audio format (webm, mp3, wav, m4a)

        Returns:
            Transcribed text

        Raises:
            Exception: If transcription fails
        """
        try:
            # Create a file-like object from bytes
            import io

            audio_file = io.BytesIO(audio_data)
            audio_file.name = f"audio.{audio_format}"

            logger.info(f"Transcribing audio ({len(audio_data)} bytes, format: {audio_format})")

            response = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
            )

            logger.info(f"Transcription successful: {response[:100]}...")

            return response

        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")

    async def analyze_food_image(
        self,
        image_data: str,
        image_format: str = "jpeg",
    ) -> Dict[str, Any]:
        """
        Analyze food image using GPT-4 Vision.

        Args:
            image_data: Base64 encoded image data
            image_format: Image format (jpeg, jpg, png, webp)

        Returns:
            Dictionary with:
                - description: Text description
                - items: List of identified food items with quantities

        Raises:
            Exception: If analysis fails
        """
        try:
            logger.info(f"Analyzing food image (format: {image_format})")

            # Prepare image URL for Vision API
            image_url = f"data:image/{image_format};base64,{image_data}"

            prompt = """
            Analyze this image and identify all food items visible.
            For each item, provide:
            1. Name of the food item
            2. Estimated quantity (with unit if possible, e.g., "2 apples", "500g chicken")
            3. Storage recommendation (pantry/fridge/freezer)
            4. Estimated shelf life in days

            Return the response in JSON format:
            {
                "description": "Brief description of what you see",
                "items": [
                    {
                        "name": "item name",
                        "quantity": 1.0,
                        "unit": "pieces",
                        "storage_location": "fridge",
                        "estimated_shelf_life_days": 7
                    }
                ]
            }

            Be practical and specific. If you can't determine exact quantity, make a reasonable estimate.
            """

            response = await self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                },
                            },
                        ],
                    }
                ],
                max_tokens=1000,
            )

            content = response.choices[0].message.content

            # Parse JSON response
            try:
                # Extract JSON from response (may have markdown code blocks)
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0].strip()
                else:
                    json_str = content

                result = json.loads(json_str)

                logger.info(f"Image analysis successful: {len(result.get('items', []))} items identified")

                return result

            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from Vision API response, returning raw description")
                return {
                    "description": content,
                    "items": [],
                }

        except Exception as e:
            logger.error(f"Food image analysis failed: {e}")
            raise Exception(f"Failed to analyze food image: {str(e)}")

    async def parse_inventory_from_text(
        self,
        text: str,
    ) -> List[Dict[str, Any]]:
        """
        Parse inventory items from natural language text.

        Args:
            text: Natural language description of items

        Returns:
            List of dictionaries with item information

        Raises:
            Exception: If parsing fails
        """
        try:
            logger.info(f"Parsing inventory items from text: {text[:100]}...")

            prompt = f"""
            Parse the following text and extract inventory items.
            For each item, provide:
            1. Name of the item
            2. Quantity (numeric value)
            3. Unit (e.g., pieces, kg, g, L, ml, boxes)
            4. Storage location (pantry/fridge/freezer) - make a reasonable guess
            5. Category (e.g., dairy, meat, vegetables, fruits, grains, etc.)

            Text: "{text}"

            Return the response in JSON format as an array:
            [
                {{
                    "name": "item name",
                    "quantity": 1.0,
                    "unit": "pieces",
                    "storage_location": "fridge",
                    "category": "dairy"
                }}
            ]

            Be practical. If quantity is not mentioned, assume 1.
            If unit is not mentioned, use "pieces".
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts structured data from natural language."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=0.3,  # Lower temperature for more consistent parsing
            )

            content = response.choices[0].message.content

            # Parse JSON response
            try:
                # Extract JSON from response
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0].strip()
                else:
                    json_str = content

                items = json.loads(json_str)

                logger.info(f"Parsed {len(items)} items from text")

                return items if isinstance(items, list) else [items]

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from GPT response: {e}")
                logger.error(f"Response content: {content}")
                return []

        except Exception as e:
            logger.error(f"Text parsing failed: {e}")
            raise Exception(f"Failed to parse inventory items: {str(e)}")

    async def analyze_nutrition(
        self,
        meal_description: str,
        portion_size: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze nutritional content of a meal.

        Args:
            meal_description: Description of the meal
            portion_size: Optional portion size description

        Returns:
            Dictionary with nutritional information

        Raises:
            Exception: If analysis fails
        """
        try:
            logger.info(f"Analyzing nutrition for: {meal_description}")

            portion_text = f" (portion: {portion_size})" if portion_size else ""
            prompt = f"""
            Analyze the nutritional content of the following meal:
            "{meal_description}"{portion_text}

            Provide detailed nutritional information in JSON format:
            {{
                "calories": 0,
                "protein_g": 0,
                "carbs_g": 0,
                "fat_g": 0,
                "fiber_g": 0,
                "sugar_g": 0,
                "sodium_mg": 0,
                "cholesterol_mg": 0,
                "vitamins": {{}},
                "minerals": {{}},
                "health_score": 0-100,
                "health_notes": "Brief health assessment"
            }}

            Be as accurate as possible based on standard nutritional data.
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a nutrition expert that provides accurate nutritional analysis."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=0.3,
            )

            content = response.choices[0].message.content

            # Parse JSON response
            try:
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0].strip()
                else:
                    json_str = content

                nutrition = json.loads(json_str)

                logger.info(f"Nutrition analysis successful: {nutrition.get('calories', 0)} calories")

                return nutrition

            except json.JSONDecodeError:
                logger.error("Failed to parse nutrition JSON")
                return {
                    "calories": 0,
                    "error": "Failed to parse nutritional data",
                }

        except Exception as e:
            logger.error(f"Nutrition analysis failed: {e}")
            raise Exception(f"Failed to analyze nutrition: {str(e)}")


# Singleton instance
openai_service = OpenAIService()
