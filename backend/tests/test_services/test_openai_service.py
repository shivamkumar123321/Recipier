"""
Tests for OpenAI service.

Tests all AI features including voice transcription, vision, text generation,
error handling, caching, and token tracking.
"""

import asyncio
import io
import json
from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from openai import APIConnectionError, APIError, RateLimitError

from app.services.openai_service import OpenAIService, OpenAIServiceError


@pytest.fixture
def openai_service():
    """Create OpenAI service instance with mocked client."""
    with patch("app.services.openai_service.AsyncOpenAI") as mock_openai:
        service = OpenAIService(api_key="test-key")
        service.client = mock_openai.return_value
        yield service


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch("app.services.openai_service.get_redis") as mock_get_redis:
        redis_mock = AsyncMock()
        mock_get_redis.return_value = redis_mock
        yield redis_mock


# ============================================================================
# Voice Transcription Tests (Whisper)
# ============================================================================


@pytest.mark.asyncio
async def test_transcribe_audio_success(openai_service):
    """Test successful audio transcription."""
    # Mock response
    openai_service.client.audio.transcriptions.create = AsyncMock(
        return_value="I have chicken, rice, and broccoli"
    )

    audio_data = b"fake audio data"
    result = await openai_service.transcribe_audio(audio_data, "webm")

    assert result == "I have chicken, rice, and broccoli"
    openai_service.client.audio.transcriptions.create.assert_called_once()


@pytest.mark.asyncio
async def test_transcribe_audio_with_language(openai_service):
    """Test audio transcription with language specification."""
    openai_service.client.audio.transcriptions.create = AsyncMock(
        return_value="Tengo pollo, arroz y brócoli"
    )

    audio_data = b"fake audio data"
    result = await openai_service.transcribe_audio(audio_data, "mp3", language="es")

    assert "pollo" in result
    call_args = openai_service.client.audio.transcriptions.create.call_args
    assert call_args[1]["language"] == "es"


@pytest.mark.asyncio
async def test_parse_inventory_from_speech(openai_service):
    """Test parsing inventory items from transcribed speech."""
    # Mock the parse_inventory_from_text method
    expected_items = [
        {
            "name": "Chicken Breast",
            "quantity": 2,
            "unit": "lbs",
            "storage_location": "refrigerator",
            "category": "protein",
        }
    ]

    with patch.object(
        openai_service, "parse_inventory_from_text", return_value=expected_items
    ):
        result = await openai_service.parse_inventory_from_speech(
            "I have two pounds of chicken breast"
        )

    assert result == expected_items


# ============================================================================
# Vision Tests (GPT-4 Vision)
# ============================================================================


@pytest.mark.asyncio
async def test_identify_food_item_success(openai_service, mock_redis):
    """Test food identification from image."""
    mock_redis.get.return_value = None  # No cache

    mock_response = Mock()
    mock_response.choices = [
        Mock(message=Mock(content='{"description": "Grilled salmon with vegetables", "items": [{"name": "salmon", "confidence": 0.95}]}'))
    ]
    mock_response.usage = Mock(total_tokens=500)

    openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    image_data = "base64encodedimage"
    result = await openai_service.identify_food_item(image_data)

    assert "description" in result
    assert "items" in result
    assert result["description"] == "Grilled salmon with vegetables"


@pytest.mark.asyncio
async def test_analyze_food_image_with_cache(openai_service, mock_redis):
    """Test food image analysis retrieves from cache."""
    cached_data = {
        "description": "Cached meal",
        "items": [{"name": "pasta", "estimated_calories": 300}],
    }
    mock_redis.get.return_value = json.dumps(cached_data).encode()

    image_data = "base64encodedimage"
    result = await openai_service.analyze_food_image(image_data)

    assert result == cached_data
    # Should not call OpenAI API
    openai_service.client.chat.completions.create.assert_not_called()


@pytest.mark.asyncio
async def test_extract_nutrition_info(openai_service, mock_redis):
    """Test extracting nutrition information from food image."""
    mock_redis.get.return_value = None

    mock_response = Mock()
    mock_response.choices = [
        Mock(
            message=Mock(
                content='{"total_calories": 450, "total_protein_g": 35, "total_carbs_g": 30, "total_fat_g": 15, "items": []}'
            )
        )
    ]
    mock_response.usage = Mock(total_tokens=600)

    openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    result = await openai_service.extract_nutrition_info("base64image")

    assert result["total_calories"] == 450
    assert result["total_protein_g"] == 35
    assert "items" in result


# ============================================================================
# Text Generation Tests (GPT-4)
# ============================================================================


@pytest.mark.asyncio
async def test_parse_inventory_from_text_success(openai_service, mock_redis):
    """Test parsing inventory from natural language text."""
    mock_redis.get.return_value = None

    mock_response = Mock()
    mock_response.choices = [
        Mock(
            message=Mock(
                content='[{"name": "Chicken Breast", "quantity": 2, "unit": "lbs", "storage_location": "refrigerator", "category": "protein"}]'
            )
        )
    ]
    mock_response.usage = Mock(total_tokens=400)

    openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    result = await openai_service.parse_inventory_from_text(
        "I have 2 pounds of chicken in the fridge"
    )

    assert len(result) == 1
    assert result[0]["name"] == "Chicken Breast"
    assert result[0]["quantity"] == 2


@pytest.mark.asyncio
async def test_generate_meal_plan_success(openai_service, mock_redis):
    """Test generating a meal plan."""
    mock_redis.get.return_value = None

    meal_plan = {
        "name": "7-Day Balanced Meal Plan",
        "days": [
            {
                "day": 1,
                "meals": [
                    {
                        "meal_type": "breakfast",
                        "name": "Oatmeal with berries",
                        "calories": 350,
                    }
                ],
            }
        ],
        "shopping_list": [{"item": "Oats", "quantity": 1, "unit": "cup"}],
    }

    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=json.dumps(meal_plan)))]
    mock_response.usage = Mock(total_tokens=1500)

    openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    inventory = [{"name": "Oats", "quantity": 2, "unit": "cups"}]
    preferences = {"cuisine": "mediterranean"}

    result = await openai_service.generate_meal_plan(
        inventory, preferences, dietary_restrictions=["vegetarian"], days=7
    )

    assert result["name"] == "7-Day Balanced Meal Plan"
    assert len(result["days"]) == 1
    assert "shopping_list" in result


@pytest.mark.asyncio
async def test_suggest_recipes_success(openai_service, mock_redis):
    """Test suggesting recipes based on ingredients."""
    mock_redis.get.return_value = None

    recipes = [
        {
            "name": "Chicken Stir Fry",
            "prep_time_minutes": 15,
            "cook_time_minutes": 20,
            "servings": 4,
            "difficulty": "easy",
            "ingredients": [{"item": "chicken", "quantity": 1, "unit": "lb"}],
            "instructions": ["Cut chicken", "Cook chicken"],
        }
    ]

    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=json.dumps(recipes)))]
    mock_response.usage = Mock(total_tokens=800)

    openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    ingredients = ["chicken", "rice", "broccoli"]
    result = await openai_service.suggest_recipes(
        ingredients, dietary_restrictions=["gluten-free"], cuisine_type="asian"
    )

    assert len(result) == 1
    assert result[0]["name"] == "Chicken Stir Fry"
    assert result[0]["difficulty"] == "easy"


@pytest.mark.asyncio
async def test_nutrition_coaching_advice(openai_service, mock_redis):
    """Test getting personalized nutrition coaching advice."""
    mock_redis.get.return_value = None

    advice = "Great job tracking your meals! I notice you're getting plenty of protein..."

    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=advice))]
    mock_response.usage = Mock(total_tokens=600)

    openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    context = {
        "recent_meals": [{"name": "Chicken Salad", "calories": 400}],
        "goals": {"target_calories": 2000, "goal_type": "weight_loss"},
    }

    result = await openai_service.nutrition_coaching_advice(context)

    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_generate_cooking_instructions(openai_service, mock_redis):
    """Test generating cooking instructions for a recipe."""
    mock_redis.get.return_value = None

    instructions = [
        "Preheat oven to 400°F",
        "Season chicken with salt and pepper",
        "Bake for 25 minutes",
    ]

    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=json.dumps(instructions)))]
    mock_response.usage = Mock(total_tokens=500)

    openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    ingredients = [{"item": "chicken breast", "quantity": 2, "unit": "pieces"}]
    result = await openai_service.generate_cooking_instructions(
        "Baked Chicken", ingredients, servings=2
    )

    assert len(result) == 3
    assert "Preheat" in result[0]


# ============================================================================
# Streaming Tests
# ============================================================================


@pytest.mark.asyncio
async def test_stream_meal_plan_generation(openai_service):
    """Test streaming meal plan generation."""

    # Mock streaming response
    async def mock_stream():
        chunks = [
            Mock(choices=[Mock(delta=Mock(content="Day 1: "))]),
            Mock(choices=[Mock(delta=Mock(content="Breakfast - "))]),
            Mock(choices=[Mock(delta=Mock(content="Oatmeal"))]),
            Mock(choices=[Mock(delta=Mock(content=None))]),  # End
        ]
        for chunk in chunks:
            yield chunk

    mock_response = MagicMock()
    mock_response.__aiter__.return_value = mock_stream()

    openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    inventory = [{"name": "Oats", "quantity": 2}]
    preferences = {"cuisine": "healthy"}

    chunks = []
    async for chunk in openai_service.stream_meal_plan_generation(
        inventory, preferences
    ):
        chunks.append(chunk)

    assert len(chunks) == 3
    assert chunks[0] == "Day 1: "
    assert chunks[1] == "Breakfast - "
    assert chunks[2] == "Oatmeal"


# ============================================================================
# Error Handling and Retry Tests
# ============================================================================


@pytest.mark.asyncio
async def test_retry_on_rate_limit(openai_service):
    """Test retry logic on rate limit errors."""
    call_count = 0

    async def mock_create(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise RateLimitError(
                "Rate limit exceeded", response=Mock(status_code=429), body=None
            )
        return Mock(
            choices=[Mock(message=Mock(content="Success"))],
            usage=Mock(total_tokens=100),
        )

    openai_service.client.chat.completions.create = mock_create

    with patch("app.services.openai_service.get_redis") as mock_get_redis:
        mock_get_redis.return_value = AsyncMock(get=AsyncMock(return_value=None))

        result = await openai_service.nutrition_coaching_advice({"test": "data"})

    assert call_count == 3
    assert result == "Success"


@pytest.mark.asyncio
async def test_no_retry_on_client_error(openai_service):
    """Test no retry on 4xx client errors."""
    openai_service.client.chat.completions.create = AsyncMock(
        side_effect=APIError(
            "Invalid request", response=Mock(status_code=400), body=None
        )
    )

    with patch("app.services.openai_service.get_redis") as mock_get_redis:
        mock_get_redis.return_value = AsyncMock(get=AsyncMock(return_value=None))

        with pytest.raises(OpenAIServiceError) as exc_info:
            await openai_service.nutrition_coaching_advice({"test": "data"})

    assert "Invalid request" in str(exc_info.value)


@pytest.mark.asyncio
async def test_max_retries_exceeded(openai_service):
    """Test failure after max retries exceeded."""
    openai_service.client.chat.completions.create = AsyncMock(
        side_effect=RateLimitError(
            "Rate limit", response=Mock(status_code=429), body=None
        )
    )

    with patch("app.services.openai_service.get_redis") as mock_get_redis:
        mock_get_redis.return_value = AsyncMock(get=AsyncMock(return_value=None))

        with pytest.raises(OpenAIServiceError) as exc_info:
            await openai_service.nutrition_coaching_advice({"test": "data"})

    assert "after 3 retries" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_connection_error_retry(openai_service):
    """Test retry on connection errors."""
    call_count = 0

    async def mock_create(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise APIConnectionError("Connection failed")
        return Mock(
            choices=[Mock(message=Mock(content="Success"))],
            usage=Mock(total_tokens=100),
        )

    openai_service.client.chat.completions.create = mock_create

    with patch("app.services.openai_service.get_redis") as mock_get_redis:
        mock_get_redis.return_value = AsyncMock(get=AsyncMock(return_value=None))

        result = await openai_service.nutrition_coaching_advice({"test": "data"})

    assert call_count == 2
    assert result == "Success"


# ============================================================================
# Caching Tests
# ============================================================================


@pytest.mark.asyncio
async def test_cache_key_generation(openai_service):
    """Test cache key generation is consistent."""
    key1 = openai_service._generate_cache_key("test", "arg1", "arg2")
    key2 = openai_service._generate_cache_key("test", "arg1", "arg2")
    key3 = openai_service._generate_cache_key("test", "arg1", "different")

    assert key1 == key2
    assert key1 != key3
    assert key1.startswith("openai:test:")


@pytest.mark.asyncio
async def test_set_cached(openai_service, mock_redis):
    """Test setting cached data in Redis."""
    data = {"test": "data"}
    cache_key = "openai:test:123"

    await openai_service._set_cached(cache_key, data)

    mock_redis.setex.assert_called_once()
    call_args = mock_redis.setex.call_args
    assert call_args[0][0] == cache_key
    assert call_args[0][1] == openai_service.cache_ttl


@pytest.mark.asyncio
async def test_get_cached_hit(openai_service, mock_redis):
    """Test getting cached data from Redis."""
    cached_data = {"cached": "response"}
    mock_redis.get.return_value = json.dumps(cached_data).encode()

    result = await openai_service._get_cached("openai:test:123")

    assert result == cached_data


@pytest.mark.asyncio
async def test_get_cached_miss(openai_service, mock_redis):
    """Test cache miss returns None."""
    mock_redis.get.return_value = None

    result = await openai_service._get_cached("openai:test:123")

    assert result is None


# ============================================================================
# Token Tracking Tests
# ============================================================================


def test_track_usage(openai_service):
    """Test token usage tracking."""
    mock_usage = Mock(total_tokens=500)

    openai_service._track_usage(mock_usage)

    assert openai_service.total_tokens_used == 500
    assert openai_service.total_requests == 1


def test_get_usage_stats(openai_service):
    """Test getting usage statistics."""
    # Simulate some usage
    openai_service.total_tokens_used = 1500
    openai_service.total_requests = 3

    stats = openai_service.get_usage_stats()

    assert stats["total_tokens_used"] == 1500
    assert stats["total_requests"] == 3
    assert stats["avg_tokens_per_request"] == 500


def test_get_usage_stats_no_requests(openai_service):
    """Test getting usage stats with no requests."""
    stats = openai_service.get_usage_stats()

    assert stats["total_tokens_used"] == 0
    assert stats["total_requests"] == 0
    assert stats["avg_tokens_per_request"] == 0


# ============================================================================
# Utility Tests
# ============================================================================


def test_parse_json_response_plain(openai_service):
    """Test parsing plain JSON response."""
    json_str = '{"key": "value"}'
    result = openai_service._parse_json_response(json_str)

    assert result == {"key": "value"}


def test_parse_json_response_markdown(openai_service):
    """Test parsing JSON from markdown code block."""
    markdown_str = '```json\n{"key": "value"}\n```'
    result = openai_service._parse_json_response(markdown_str)

    assert result == {"key": "value"}


def test_parse_json_response_code_block(openai_service):
    """Test parsing JSON from generic code block."""
    code_block = '```\n{"key": "value"}\n```'
    result = openai_service._parse_json_response(code_block)

    assert result == {"key": "value"}


def test_parse_json_response_array(openai_service):
    """Test parsing JSON array."""
    json_str = '[{"item": 1}, {"item": 2}]'
    result = openai_service._parse_json_response(json_str)

    assert len(result) == 2
    assert result[0]["item"] == 1


def test_parse_json_response_invalid(openai_service):
    """Test parsing invalid JSON raises error."""
    invalid_json = "not valid json"

    with pytest.raises(OpenAIServiceError) as exc_info:
        openai_service._parse_json_response(invalid_json)

    assert "Failed to parse JSON" in str(exc_info.value)


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.asyncio
async def test_full_workflow_with_cache(openai_service, mock_redis):
    """Test full workflow with caching enabled."""
    # First call - cache miss
    mock_redis.get.return_value = None

    mock_response = Mock()
    mock_response.choices = [
        Mock(message=Mock(content='[{"name": "Chicken", "quantity": 1}]'))
    ]
    mock_response.usage = Mock(total_tokens=300)

    openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    result1 = await openai_service.parse_inventory_from_text("I have chicken")

    # Verify API was called
    assert openai_service.client.chat.completions.create.call_count == 1

    # Second call - cache hit
    mock_redis.get.return_value = json.dumps(result1).encode()

    result2 = await openai_service.parse_inventory_from_text("I have chicken")

    # Verify API was not called again
    assert openai_service.client.chat.completions.create.call_count == 1
    assert result1 == result2
