"""
Comprehensive OpenAI service for AI-powered features.

Provides:
- Speech-to-text (Whisper)
- Image recognition (GPT-4 Vision)
- Text generation (GPT-4): meal plans, recipes, coaching
- Streaming support for real-time responses
- Error handling with exponential backoff retry
- Token usage tracking
- Redis caching for repeated queries
"""

import asyncio
import base64
import hashlib
import io
import json
from typing import Any, AsyncIterator, Dict, List, Optional

import openai
from openai import AsyncOpenAI, APIError, RateLimitError, APIConnectionError

from app.core.cache import get_redis
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIServiceError(Exception):
    """Base exception for OpenAI service errors."""
    pass


class OpenAIService:
    """Comprehensive service for OpenAI API interactions."""

    def __init__(self):
        """Initialize OpenAI client with configuration."""
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=settings.OPENAI_TIMEOUT,
            max_retries=0,  # We handle retries manually
        )
        self.model = settings.OPENAI_MODEL
        self.vision_model = settings.OPENAI_VISION_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
        self.max_retries = settings.OPENAI_MAX_RETRIES
        self.cache_ttl = settings.OPENAI_CACHE_TTL
        self.enable_caching = settings.OPENAI_ENABLE_CACHING
        self.track_usage = settings.OPENAI_TRACK_USAGE

        # Token usage tracking
        self.total_tokens_used = 0
        self.total_requests = 0

    # ==================== Error Handling & Retry Logic ====================

    async def _retry_with_backoff(
        self,
        func,
        *args,
        **kwargs,
    ) -> Any:
        """
        Retry a function with exponential backoff.

        Args:
            func: Async function to retry
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            OpenAIServiceError: If all retries fail
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)

            except RateLimitError as e:
                last_error = e
                wait_time = (2 ** attempt) * 1  # 1s, 2s, 4s
                logger.warning(
                    f"Rate limit exceeded (attempt {attempt + 1}/{self.max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)

            except APIConnectionError as e:
                last_error = e
                wait_time = (2 ** attempt) * 1
                logger.warning(
                    f"API connection error (attempt {attempt + 1}/{self.max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)

            except APIError as e:
                last_error = e
                # Don't retry on client errors (4xx)
                if hasattr(e, 'status_code') and 400 <= e.status_code < 500:
                    logger.error(f"Client error (no retry): {e}")
                    raise OpenAIServiceError(f"OpenAI API error: {str(e)}")

                wait_time = (2 ** attempt) * 1
                logger.warning(
                    f"API error (attempt {attempt + 1}/{self.max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)

            except Exception as e:
                logger.error(f"Unexpected error in OpenAI request: {e}", exc_info=True)
                raise OpenAIServiceError(f"Unexpected error: {str(e)}")

        # All retries failed
        logger.error(f"All {self.max_retries} retry attempts failed")
        raise OpenAIServiceError(f"OpenAI API request failed after {self.max_retries} retries: {str(last_error)}")

    # ==================== Caching ====================

    def _generate_cache_key(self, prefix: str, *args) -> str:
        """
        Generate cache key from arguments.

        Args:
            prefix: Cache key prefix
            *args: Arguments to hash

        Returns:
            Cache key string
        """
        content = json.dumps(args, sort_keys=True)
        hash_value = hashlib.md5(content.encode()).hexdigest()
        return f"openai:{prefix}:{hash_value}"

    async def _get_cached(self, cache_key: str) -> Optional[Any]:
        """Get cached response."""
        if not self.enable_caching:
            return None

        try:
            redis = await get_redis()
            cached = await redis.get(cache_key)
            if cached:
                logger.debug(f"Cache hit: {cache_key}")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")

        return None

    async def _set_cached(self, cache_key: str, value: Any) -> None:
        """Set cached response."""
        if not self.enable_caching:
            return

        try:
            redis = await get_redis()
            await redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(value),
            )
            logger.debug(f"Cache set: {cache_key} (TTL: {self.cache_ttl}s)")
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")

    # ==================== Token Tracking ====================

    def _track_usage(self, usage: Any) -> None:
        """Track token usage."""
        if not self.track_usage or not usage:
            return

        try:
            total_tokens = usage.total_tokens
            self.total_tokens_used += total_tokens
            self.total_requests += 1

            logger.info(
                f"OpenAI API usage: {total_tokens} tokens "
                f"(Total: {self.total_tokens_used} tokens, "
                f"{self.total_requests} requests)"
            )
        except Exception as e:
            logger.warning(f"Token tracking failed: {e}")

    def get_usage_stats(self) -> Dict[str, int]:
        """
        Get token usage statistics.

        Returns:
            Dictionary with total_tokens_used and total_requests
        """
        return {
            "total_tokens_used": self.total_tokens_used,
            "total_requests": self.total_requests,
            "avg_tokens_per_request": (
                self.total_tokens_used // self.total_requests
                if self.total_requests > 0
                else 0
            ),
        }

    # ==================== Voice Transcription (Whisper) ====================

    async def transcribe_audio(
        self,
        audio_data: bytes,
        audio_format: str = "webm",
        language: Optional[str] = None,
    ) -> str:
        """
        Transcribe audio to text using Whisper.

        Args:
            audio_data: Audio file bytes
            audio_format: Audio format (webm, mp3, wav, m4a, etc.)
            language: Optional language code (e.g., 'en', 'es', 'fr')

        Returns:
            Transcribed text

        Raises:
            OpenAIServiceError: If transcription fails

        Example:
            >>> with open("audio.mp3", "rb") as f:
            ...     text = await service.transcribe_audio(f.read(), "mp3")
            >>> print(text)
            "I need to buy milk, eggs, and bread"
        """
        logger.info(f"Transcribing audio ({len(audio_data)} bytes, format: {audio_format})")

        async def _transcribe():
            audio_file = io.BytesIO(audio_data)
            audio_file.name = f"audio.{audio_format}"

            params = {
                "model": "whisper-1",
                "file": audio_file,
                "response_format": "text",
            }

            if language:
                params["language"] = language

            response = await self.client.audio.transcriptions.create(**params)
            return response

        try:
            text = await self._retry_with_backoff(_transcribe)
            logger.info(f"Transcription successful: '{text[:100]}...'")
            return text

        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            raise OpenAIServiceError(f"Failed to transcribe audio: {str(e)}")

    async def parse_inventory_from_speech(
        self,
        transcribed_text: str,
    ) -> List[Dict[str, Any]]:
        """
        Parse inventory items from transcribed speech.

        Args:
            transcribed_text: Transcribed text from Whisper

        Returns:
            List of inventory items with structured data

        Example:
            >>> text = "I bought 2 pounds of chicken, a dozen eggs, and 3 tomatoes"
            >>> items = await service.parse_inventory_from_speech(text)
            >>> print(items)
            [{"name": "chicken", "quantity": 2, "unit": "pounds", ...}, ...]
        """
        return await self.parse_inventory_from_text(transcribed_text)

    # ==================== Vision (Food Recognition) ====================

    async def identify_food_item(
        self,
        image_data: str,
        image_format: str = "jpeg",
    ) -> Dict[str, Any]:
        """
        Identify food items in an image using GPT-4 Vision.

        Args:
            image_data: Base64 encoded image data
            image_format: Image format (jpeg, jpg, png, webp)

        Returns:
            Dictionary with food items and metadata

        Raises:
            OpenAIServiceError: If identification fails

        Example:
            >>> with open("food.jpg", "rb") as f:
            ...     b64_data = base64.b64encode(f.read()).decode()
            >>> result = await service.identify_food_item(b64_data, "jpeg")
            >>> print(result)
            {"items": [{"name": "Apple", "quantity": 3, ...}], ...}
        """
        return await self.analyze_food_image(image_data, image_format)

    async def analyze_food_image(
        self,
        image_data: str,
        image_format: str = "jpeg",
    ) -> Dict[str, Any]:
        """
        Analyze food image using GPT-4 Vision with detailed nutritional info.

        Args:
            image_data: Base64 encoded image data
            image_format: Image format (jpeg, jpg, png, webp)

        Returns:
            Dictionary with description, items, and nutritional estimates
        """
        cache_key = self._generate_cache_key("vision", image_data[:100], image_format)

        # Check cache
        cached = await self._get_cached(cache_key)
        if cached:
            return cached

        logger.info(f"Analyzing food image (format: {image_format})")

        image_url = f"data:image/{image_format};base64,{image_data}"

        prompt = """
        Analyze this image and identify all food items visible.
        For each item, provide:
        1. Name of the food item
        2. Estimated quantity (with unit if possible, e.g., "2 apples", "500g chicken")
        3. Storage recommendation (pantry/fridge/freezer)
        4. Estimated shelf life in days
        5. Category (fruits, vegetables, dairy, meat, grains, etc.)

        Return the response in JSON format:
        {
            "description": "Brief description of what you see",
            "items": [
                {
                    "name": "item name",
                    "quantity": 1.0,
                    "unit": "pieces",
                    "storage_location": "fridge",
                    "estimated_shelf_life_days": 7,
                    "category": "fruits"
                }
            ]
        }

        Be practical and specific. If you can't determine exact quantity, make a reasonable estimate.
        """

        async def _analyze():
            response = await self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url},
                            },
                        ],
                    }
                ],
                max_tokens=1000,
                temperature=0.3,
            )

            self._track_usage(response.usage)
            return response.choices[0].message.content

        try:
            content = await self._retry_with_backoff(_analyze)

            # Parse JSON response
            result = self._parse_json_response(content)

            logger.info(f"Image analysis successful: {len(result.get('items', []))} items identified")

            # Cache result
            await self._set_cached(cache_key, result)

            return result

        except Exception as e:
            logger.error(f"Food image analysis failed: {e}")
            raise OpenAIServiceError(f"Failed to analyze food image: {str(e)}")

    async def extract_nutrition_info(
        self,
        image_data: str,
        image_format: str = "jpeg",
    ) -> Dict[str, Any]:
        """
        Extract nutritional information from food image.

        Args:
            image_data: Base64 encoded image data
            image_format: Image format

        Returns:
            Dictionary with estimated nutritional information

        Example:
            >>> nutrition = await service.extract_nutrition_info(image_b64, "jpeg")
            >>> print(nutrition["total_calories"])
            450
        """
        cache_key = self._generate_cache_key("nutrition_vision", image_data[:100])

        # Check cache
        cached = await self._get_cached(cache_key)
        if cached:
            return cached

        logger.info("Extracting nutrition info from image")

        image_url = f"data:image/{image_format};base64,{image_data}"

        prompt = """
        Analyze this food image and estimate the nutritional content.
        Provide estimates for the visible food items.

        Return in JSON format:
        {
            "total_calories": 0,
            "total_protein_g": 0,
            "total_carbs_g": 0,
            "total_fat_g": 0,
            "items": [
                {
                    "name": "item",
                    "calories": 0,
                    "protein_g": 0,
                    "carbs_g": 0,
                    "fat_g": 0
                }
            ]
        }
        """

        async def _extract():
            response = await self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
                max_tokens=800,
                temperature=0.3,
            )

            self._track_usage(response.usage)
            return response.choices[0].message.content

        try:
            content = await self._retry_with_backoff(_extract)
            result = self._parse_json_response(content)

            await self._set_cached(cache_key, result)

            return result

        except Exception as e:
            logger.error(f"Nutrition extraction failed: {e}")
            raise OpenAIServiceError(f"Failed to extract nutrition info: {str(e)}")

    # ==================== Text Generation (GPT-4) ====================

    async def parse_inventory_from_text(
        self,
        text: str,
    ) -> List[Dict[str, Any]]:
        """
        Parse inventory items from natural language text.

        Args:
            text: Natural language description of items

        Returns:
            List of inventory items with structured data

        Example:
            >>> items = await service.parse_inventory_from_text(
            ...     "I bought 2kg chicken, 500g tomatoes, and a dozen eggs"
            ... )
        """
        cache_key = self._generate_cache_key("parse_inventory", text)

        # Check cache
        cached = await self._get_cached(cache_key)
        if cached:
            return cached

        logger.info(f"Parsing inventory items from text: '{text[:100]}...'")

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

        async def _parse():
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts structured data from natural language. Always respond with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=0.3,
            )

            self._track_usage(response.usage)
            return response.choices[0].message.content

        try:
            content = await self._retry_with_backoff(_parse)
            items = self._parse_json_response(content)

            # Ensure it's a list
            if not isinstance(items, list):
                items = [items]

            logger.info(f"Parsed {len(items)} items from text")

            await self._set_cached(cache_key, items)

            return items

        except Exception as e:
            logger.error(f"Text parsing failed: {e}")
            raise OpenAIServiceError(f"Failed to parse inventory items: {str(e)}")

    async def generate_meal_plan(
        self,
        inventory: List[Dict[str, Any]],
        preferences: Dict[str, Any],
        dietary_restrictions: Optional[List[str]] = None,
        target_calories: Optional[int] = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Generate AI-powered meal plan based on inventory and preferences.

        Args:
            inventory: List of available inventory items
            preferences: User preferences (cuisine, meal types, etc.)
            dietary_restrictions: List of dietary restrictions
            target_calories: Daily calorie target
            days: Number of days to plan

        Returns:
            Dictionary with meal plan structure

        Raises:
            OpenAIServiceError: If generation fails

        Example:
            >>> inventory = [
            ...     {"name": "chicken", "quantity": 1, "unit": "kg"},
            ...     {"name": "rice", "quantity": 500, "unit": "g"},
            ... ]
            >>> preferences = {"cuisine": "italian", "meal_types": ["lunch", "dinner"]}
            >>> plan = await service.generate_meal_plan(
            ...     inventory, preferences, ["vegetarian"], 2000, 7
            ... )
        """
        cache_key = self._generate_cache_key(
            "meal_plan",
            inventory,
            preferences,
            dietary_restrictions,
            target_calories,
            days,
        )

        # Check cache
        cached = await self._get_cached(cache_key)
        if cached:
            return cached

        logger.info(f"Generating {days}-day meal plan")

        restrictions_text = ", ".join(dietary_restrictions) if dietary_restrictions else "none"
        inventory_text = "\n".join([f"- {item['name']} ({item.get('quantity', 1)} {item.get('unit', 'units')})" for item in inventory[:20]])

        prompt = f"""
        Create a {days}-day meal plan based on the following:

        **Available Inventory:**
        {inventory_text}

        **Dietary Restrictions:** {restrictions_text}
        **Target Calories:** {target_calories or 'flexible'} per day
        **Preferences:** {json.dumps(preferences)}

        Generate a meal plan that:
        1. Prioritizes using available inventory items
        2. Respects dietary restrictions
        3. Balances nutrition across meals
        4. Includes breakfast, lunch, and dinner
        5. Provides variety across days

        Return in JSON format:
        {{
            "name": "meal plan name",
            "summary": "brief description",
            "days": [
                {{
                    "day": 1,
                    "date": "2025-11-18",
                    "total_calories": 2000,
                    "meals": [
                        {{
                            "meal_type": "breakfast",
                            "recipe_name": "name",
                            "description": "brief description",
                            "calories": 500,
                            "ingredients": ["ingredient1", "ingredient2"],
                            "prep_time_minutes": 15
                        }}
                    ]
                }}
            ],
            "shopping_list": [
                {{
                    "name": "item",
                    "quantity": 1,
                    "unit": "pieces"
                }}
            ]
        }}
        """

        async def _generate():
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional nutritionist and meal planning expert. Create balanced, healthy meal plans."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=4000,
                temperature=0.8,
            )

            self._track_usage(response.usage)
            return response.choices[0].message.content

        try:
            content = await self._retry_with_backoff(_generate)
            meal_plan = self._parse_json_response(content)

            logger.info(f"Meal plan generated with {len(meal_plan.get('days', []))} days")

            await self._set_cached(cache_key, meal_plan)

            return meal_plan

        except Exception as e:
            logger.error(f"Meal plan generation failed: {e}")
            raise OpenAIServiceError(f"Failed to generate meal plan: {str(e)}")

    async def suggest_recipes(
        self,
        ingredients: List[str],
        dietary_restrictions: Optional[List[str]] = None,
        cuisine_type: Optional[str] = None,
        max_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Suggest recipes based on available ingredients.

        Args:
            ingredients: List of available ingredients
            dietary_restrictions: Optional dietary restrictions
            cuisine_type: Optional cuisine preference
            max_results: Maximum number of recipes to return

        Returns:
            List of recipe suggestions

        Example:
            >>> recipes = await service.suggest_recipes(
            ...     ["chicken", "rice", "tomatoes"],
            ...     ["gluten-free"],
            ...     "italian",
            ...     5
            ... )
        """
        cache_key = self._generate_cache_key(
            "suggest_recipes",
            ingredients,
            dietary_restrictions,
            cuisine_type,
        )

        # Check cache
        cached = await self._get_cached(cache_key)
        if cached:
            return cached[:max_results]

        logger.info(f"Suggesting recipes for {len(ingredients)} ingredients")

        restrictions_text = ", ".join(dietary_restrictions) if dietary_restrictions else "none"
        ingredients_text = ", ".join(ingredients)
        cuisine_text = cuisine_type or "any cuisine"

        prompt = f"""
        Suggest {max_results} recipes using these ingredients: {ingredients_text}

        **Dietary Restrictions:** {restrictions_text}
        **Cuisine Type:** {cuisine_text}

        Return in JSON format as an array:
        [
            {{
                "name": "recipe name",
                "description": "brief description",
                "difficulty": "easy|medium|hard",
                "prep_time_minutes": 30,
                "cook_time_minutes": 45,
                "servings": 4,
                "calories_per_serving": 500,
                "ingredients": [
                    {{
                        "name": "ingredient",
                        "quantity": 1,
                        "unit": "cup"
                    }}
                ],
                "instructions": ["step 1", "step 2", "step 3"]
            }}
        ]
        """

        async def _suggest():
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a creative chef who creates delicious, practical recipes."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=3000,
                temperature=0.9,
            )

            self._track_usage(response.usage)
            return response.choices[0].message.content

        try:
            content = await self._retry_with_backoff(_suggest)
            recipes = self._parse_json_response(content)

            # Ensure it's a list
            if not isinstance(recipes, list):
                recipes = [recipes]

            logger.info(f"Suggested {len(recipes)} recipes")

            await self._set_cached(cache_key, recipes)

            return recipes[:max_results]

        except Exception as e:
            logger.error(f"Recipe suggestion failed: {e}")
            raise OpenAIServiceError(f"Failed to suggest recipes: {str(e)}")

    async def nutrition_coaching_advice(
        self,
        context: Dict[str, Any],
    ) -> str:
        """
        Get personalized nutrition coaching advice.

        Args:
            context: User context including:
                - user_goals: weight loss, muscle gain, etc.
                - recent_meals: list of recent meals
                - current_stats: weight, height, activity level
                - preferences: dietary preferences

        Returns:
            Personalized coaching advice text

        Example:
            >>> context = {
            ...     "user_goals": "weight loss",
            ...     "recent_meals": ["pizza", "burger", "salad"],
            ...     "current_stats": {"weight_kg": 75, "height_cm": 170},
            ... }
            >>> advice = await service.nutrition_coaching_advice(context)
        """
        logger.info("Generating nutrition coaching advice")

        prompt = f"""
        As a professional nutrition coach, provide personalized advice based on:

        **User Context:**
        {json.dumps(context, indent=2)}

        Provide:
        1. Assessment of recent eating habits
        2. Specific recommendations for improvement
        3. Practical tips for achieving goals
        4. Motivational support

        Keep the advice friendly, practical, and actionable.
        Format as clear paragraphs, not JSON.
        """

        async def _coach():
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a supportive, knowledgeable nutrition coach who provides personalized, evidence-based advice."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1500,
                temperature=0.7,
            )

            self._track_usage(response.usage)
            return response.choices[0].message.content

        try:
            advice = await self._retry_with_backoff(_coach)

            logger.info("Coaching advice generated successfully")

            return advice

        except Exception as e:
            logger.error(f"Coaching advice generation failed: {e}")
            raise OpenAIServiceError(f"Failed to generate coaching advice: {str(e)}")

    async def generate_cooking_instructions(
        self,
        recipe_name: str,
        ingredients: List[Dict[str, Any]],
        servings: int = 4,
    ) -> List[str]:
        """
        Generate detailed cooking instructions for a recipe.

        Args:
            recipe_name: Name of the recipe
            ingredients: List of ingredients with quantities
            servings: Number of servings

        Returns:
            List of step-by-step cooking instructions

        Example:
            >>> instructions = await service.generate_cooking_instructions(
            ...     "Chicken Stir Fry",
            ...     [{"name": "chicken", "quantity": 500, "unit": "g"}],
            ...     4
            ... )
        """
        cache_key = self._generate_cache_key(
            "cooking_instructions",
            recipe_name,
            ingredients,
            servings,
        )

        # Check cache
        cached = await self._get_cached(cache_key)
        if cached:
            return cached

        logger.info(f"Generating cooking instructions for {recipe_name}")

        ingredients_text = "\n".join([f"- {ing['name']}: {ing.get('quantity', 1)} {ing.get('unit', 'units')}" for ing in ingredients])

        prompt = f"""
        Create detailed cooking instructions for: {recipe_name}
        Servings: {servings}

        **Ingredients:**
        {ingredients_text}

        Provide step-by-step instructions that are:
        1. Clear and easy to follow
        2. Include preparation and cooking steps
        3. Specify cooking times and temperatures
        4. Include plating/serving suggestions

        Return as a JSON array of instruction strings:
        ["Step 1: ...", "Step 2: ...", "Step 3: ..."]
        """

        async def _generate():
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional chef who writes clear, detailed cooking instructions."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
                temperature=0.7,
            )

            self._track_usage(response.usage)
            return response.choices[0].message.content

        try:
            content = await self._retry_with_backoff(_generate)
            instructions = self._parse_json_response(content)

            # Ensure it's a list
            if not isinstance(instructions, list):
                instructions = [str(instructions)]

            logger.info(f"Generated {len(instructions)} cooking steps")

            await self._set_cached(cache_key, instructions)

            return instructions

        except Exception as e:
            logger.error(f"Cooking instructions generation failed: {e}")
            raise OpenAIServiceError(f"Failed to generate cooking instructions: {str(e)}")

    # ==================== Streaming Support ====================

    async def stream_meal_plan_generation(
        self,
        inventory: List[Dict[str, Any]],
        preferences: Dict[str, Any],
        dietary_restrictions: Optional[List[str]] = None,
        target_calories: Optional[int] = None,
        days: int = 7,
    ) -> AsyncIterator[str]:
        """
        Stream meal plan generation with real-time updates.

        Args:
            inventory: Available inventory items
            preferences: User preferences
            dietary_restrictions: Dietary restrictions
            target_calories: Daily calorie target
            days: Number of days

        Yields:
            Streaming response chunks

        Example:
            >>> async for chunk in service.stream_meal_plan_generation(...):
            ...     print(chunk, end="", flush=True)
        """
        logger.info(f"Streaming {days}-day meal plan generation")

        restrictions_text = ", ".join(dietary_restrictions) if dietary_restrictions else "none"
        inventory_text = "\n".join([f"- {item['name']}" for item in inventory[:20]])

        prompt = f"""
        Create a {days}-day meal plan.

        **Inventory:** {inventory_text}
        **Dietary Restrictions:** {restrictions_text}
        **Target Calories:** {target_calories or 'flexible'} per day

        Provide a detailed meal plan with breakfast, lunch, and dinner for each day.
        """

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional meal planning expert."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=4000,
                temperature=0.8,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

            logger.info("Streaming meal plan generation completed")

        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            raise OpenAIServiceError(f"Failed to stream meal plan: {str(e)}")

    # ==================== Utility Functions ====================

    def _parse_json_response(self, content: str) -> Any:
        """
        Parse JSON from GPT response, handling code blocks.

        Args:
            content: Response content

        Returns:
            Parsed JSON object

        Raises:
            ValueError: If JSON parsing fails
        """
        try:
            # Remove markdown code blocks if present
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            return json.loads(json_str)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Content: {content[:500]}")
            raise ValueError(f"Invalid JSON response from OpenAI: {str(e)}")

    async def text_to_speech(
        self,
        text: str,
        voice: str = "nova",
        model: str = "tts-1",
        response_format: str = "mp3",
    ) -> bytes:
        """
        Convert text to speech using OpenAI TTS.

        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            model: TTS model (tts-1 or tts-1-hd)
            response_format: Audio format (mp3, opus, aac, flac, wav, pcm)

        Returns:
            Audio data in bytes

        Raises:
            OpenAIServiceError: If TTS generation fails

        Example:
            >>> audio_bytes = await service.text_to_speech(
            ...     "Hello! Your timer is done.",
            ...     voice="nova"
            ... )
            >>> with open("response.mp3", "wb") as f:
            ...     f.write(audio_bytes)
        """
        logger.info(f"Generating TTS for text: '{text[:50]}...' (voice: {voice})")

        async def _generate_speech():
            response = await self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                response_format=response_format,
            )

            # Read the audio content
            audio_data = b""
            async for chunk in response.iter_bytes():
                audio_data += chunk

            return audio_data

        try:
            audio_bytes = await self._retry_with_backoff(_generate_speech)
            logger.info(f"TTS successful: {len(audio_bytes)} bytes generated")
            return audio_bytes

        except Exception as e:
            logger.error(f"Text-to-speech failed: {e}", exc_info=True)
            raise OpenAIServiceError(f"TTS generation failed: {str(e)}")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
    ) -> str:
        """
        Simple chat completion without streaming.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            model: Model to use (defaults to configured model)

        Returns:
            Response text

        Raises:
            OpenAIServiceError: If completion fails
        """
        async def _complete():
            response = await self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )

            # Track usage
            if self.track_usage and hasattr(response, 'usage'):
                self.total_tokens_used += response.usage.total_tokens
                self.total_requests += 1

            return response.choices[0].message.content

        try:
            return await self._retry_with_backoff(_complete)
        except Exception as e:
            logger.error(f"Chat completion failed: {e}", exc_info=True)
            raise OpenAIServiceError(f"Chat completion failed: {str(e)}")


# Singleton instance
openai_service = OpenAIService()


def get_openai_service() -> OpenAIService:
    """Get OpenAI service singleton instance."""
    return openai_service
