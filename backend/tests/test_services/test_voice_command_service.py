"""
Tests for voice command service with prompt engineering.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.voice_command_service import (
    VoiceCommandResult,
    VoiceCommandService,
    VoiceCommandType,
)
from tests.fixtures.audio_samples import (
    EXPECTED_EXPIRATION_QUERIES,
    EXPECTED_PARSED_ITEMS,
    EXPECTED_RECIPE_INGREDIENTS,
    SAMPLE_ADD_ITEMS_TRANSCRIPTIONS,
    SAMPLE_EXPIRATION_CHECK_TRANSCRIPTIONS,
    SAMPLE_RECIPE_QUERY_TRANSCRIPTIONS,
    SAMPLE_SEARCH_INVENTORY_TRANSCRIPTIONS,
)


@pytest.fixture
def mock_openai_service():
    """Create mock OpenAI service."""
    service = Mock()
    service.client = Mock()
    service._parse_json_response = Mock(side_effect=lambda x: __import__('json').loads(x.strip('```json').strip('```').strip()))
    return service


@pytest.fixture
def voice_service(mock_openai_service):
    """Create voice command service with mocked OpenAI."""
    return VoiceCommandService(mock_openai_service)


# Intent Classification Tests


@pytest.mark.asyncio
async def test_classify_intent_add_items(voice_service, mock_openai_service):
    """Test classifying add items intent."""
    # Mock GPT response
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="add_items"))]

    mock_openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    intent = await voice_service.classify_intent("Add 3 apples and 2 bananas")

    assert intent == VoiceCommandType.ADD_ITEMS


@pytest.mark.asyncio
async def test_classify_intent_query_recipes(voice_service, mock_openai_service):
    """Test classifying recipe query intent."""
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="query_recipes"))]

    mock_openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    intent = await voice_service.classify_intent(
        "What can I cook with chicken and rice?"
    )

    assert intent == VoiceCommandType.QUERY_RECIPES


@pytest.mark.asyncio
async def test_classify_intent_check_expiration(voice_service, mock_openai_service):
    """Test classifying expiration check intent."""
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="check_expiration"))]

    mock_openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    intent = await voice_service.classify_intent("When does my milk expire?")

    assert intent == VoiceCommandType.CHECK_EXPIRATION


@pytest.mark.asyncio
async def test_classify_intent_search_inventory(voice_service, mock_openai_service):
    """Test classifying search inventory intent."""
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="search_inventory"))]

    mock_openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    intent = await voice_service.classify_intent("Show me all vegetables")

    assert intent == VoiceCommandType.SEARCH_INVENTORY


@pytest.mark.asyncio
async def test_classify_intent_unknown(voice_service, mock_openai_service):
    """Test classifying unknown intent."""
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="unknown"))]

    mock_openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    intent = await voice_service.classify_intent("Tell me a joke")

    assert intent == VoiceCommandType.UNKNOWN


# Item Extraction Tests


@pytest.mark.asyncio
async def test_extract_items_from_text(voice_service, mock_openai_service):
    """Test extracting inventory items from text."""
    text = "Add 3 apples and 2 pounds of chicken"
    expected = EXPECTED_PARSED_ITEMS[text]

    import json
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=json.dumps(expected)))]

    mock_openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    items = await voice_service._extract_items_from_text(text)

    assert len(items) == 2
    assert items[0]["name"] == "Apple"
    assert items[0]["quantity"] == 3
    assert items[1]["name"] == "Chicken"
    assert items[1]["quantity"] == 2


@pytest.mark.asyncio
async def test_extract_items_complex_text(voice_service, mock_openai_service):
    """Test extracting items from complex text."""
    text = "I bought milk, eggs, and a bag of rice"
    expected = EXPECTED_PARSED_ITEMS[text]

    import json
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=json.dumps(expected)))]

    mock_openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    items = await voice_service._extract_items_from_text(text)

    assert len(items) == 3
    assert any(item["name"] == "Milk" for item in items)
    assert any(item["name"] == "Eggs" for item in items)
    assert any(item["name"] == "Rice" for item in items)


# Recipe Ingredient Extraction Tests


@pytest.mark.asyncio
async def test_extract_recipe_ingredients(voice_service, mock_openai_service):
    """Test extracting ingredients from recipe query."""
    text = "What can I cook with chicken and rice?"
    expected = EXPECTED_RECIPE_INGREDIENTS[text]

    import json
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=json.dumps(expected)))]

    mock_openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    ingredients = await voice_service._extract_recipe_ingredients(text)

    assert len(ingredients) == 2
    assert "chicken" in ingredients
    assert "rice" in ingredients


@pytest.mark.asyncio
async def test_extract_recipe_ingredients_multiple(voice_service, mock_openai_service):
    """Test extracting multiple ingredients."""
    text = "I have tomatoes, onions, and garlic. What can I make?"
    expected = EXPECTED_RECIPE_INGREDIENTS[text]

    import json
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=json.dumps(expected)))]

    mock_openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    ingredients = await voice_service._extract_recipe_ingredients(text)

    assert len(ingredients) == 3
    assert "tomatoes" in ingredients
    assert "onions" in ingredients
    assert "garlic" in ingredients


# Expiration Query Extraction Tests


@pytest.mark.asyncio
async def test_extract_expiration_query_specific_item(
    voice_service, mock_openai_service
):
    """Test extracting expiration query for specific item."""
    text = "When does my milk expire?"
    expected = EXPECTED_EXPIRATION_QUERIES[text]

    import json
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=json.dumps(expected)))]

    mock_openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    query = await voice_service._extract_expiration_query(text)

    assert query["item"] == "milk"
    assert query["days"] is None


@pytest.mark.asyncio
async def test_extract_expiration_query_with_days(
    voice_service, mock_openai_service
):
    """Test extracting expiration query with days specified."""
    text = "What's expiring within 3 days?"
    expected = EXPECTED_EXPIRATION_QUERIES[text]

    import json
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=json.dumps(expected)))]

    mock_openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    query = await voice_service._extract_expiration_query(text)

    assert query["item"] is None
    assert query["days"] == 3


# Search Query Extraction Tests


def test_extract_search_query_simple(voice_service):
    """Test extracting simple search query."""
    text = "Show me all vegetables"
    query = voice_service._extract_search_query(text)

    assert query == "vegetables"


def test_extract_search_query_complex(voice_service):
    """Test extracting complex search query."""
    text = "What fruits do I have in my inventory"
    query = voice_service._extract_search_query(text)

    assert query == "fruits"


def test_extract_search_query_no_match(voice_service):
    """Test search query extraction with no match."""
    text = "Tell me about weather"
    query = voice_service._extract_search_query(text)

    assert query is None


# Command Processing Tests


@pytest.mark.asyncio
async def test_process_add_items_command(
    voice_service, mock_openai_service, db: AsyncSession, verified_user: User
):
    """Test processing add items command."""
    text = "Add 3 apples"

    # Mock item extraction
    import json
    mock_response = Mock()
    mock_response.choices = [
        Mock(
            message=Mock(
                content=json.dumps([
                    {
                        "name": "Apple",
                        "quantity": 3,
                        "unit": "items",
                        "storage_location": "pantry",
                    }
                ])
            )
        )
    ]

    mock_openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    result = await voice_service.process_add_items_command(
        text, db, verified_user.id
    )

    assert result.command_type == VoiceCommandType.ADD_ITEMS
    assert result.success is True
    assert "items" in result.data


@pytest.mark.asyncio
async def test_process_add_items_command_no_items(
    voice_service, mock_openai_service, db: AsyncSession, verified_user: User
):
    """Test processing add items command with no extractable items."""
    text = "Hello there"

    # Mock empty extraction
    import json
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=json.dumps([])))]

    mock_openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    result = await voice_service.process_add_items_command(
        text, db, verified_user.id
    )

    assert result.success is False
    assert "No items could be extracted" in result.message


@pytest.mark.asyncio
async def test_process_recipe_query_command(
    voice_service, mock_openai_service, db: AsyncSession, verified_user: User
):
    """Test processing recipe query command."""
    text = "What can I cook with chicken?"

    # Mock ingredient extraction
    import json
    mock_extract_response = Mock()
    mock_extract_response.choices = [
        Mock(message=Mock(content=json.dumps(["chicken"])))
    ]

    # Mock recipe suggestion
    recipes = [
        {
            "name": "Grilled Chicken",
            "prep_time_minutes": 15,
            "instructions": ["Cook chicken"],
        }
    ]
    mock_openai_service.suggest_recipes = AsyncMock(return_value=recipes)

    mock_openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_extract_response
    )

    result = await voice_service.process_recipe_query_command(
        text, db, verified_user.id
    )

    assert result.command_type == VoiceCommandType.QUERY_RECIPES
    assert result.success is True
    assert "recipes" in result.data
    assert len(result.data["recipes"]) == 1


@pytest.mark.asyncio
async def test_process_unknown_command(
    voice_service, mock_openai_service, db: AsyncSession, verified_user: User
):
    """Test processing unknown command type."""
    text = "Tell me a joke"

    # Mock intent classification
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="unknown"))]

    mock_openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    result = await voice_service.process_voice_command(
        text, db, verified_user.id
    )

    assert result.command_type == VoiceCommandType.UNKNOWN
    assert result.success is False
    assert "didn't understand" in result.message


# Error Handling Tests


@pytest.mark.asyncio
async def test_classify_intent_error_handling(voice_service, mock_openai_service):
    """Test intent classification with error."""
    mock_openai_service.client.chat.completions.create = AsyncMock(
        side_effect=Exception("API Error")
    )

    intent = await voice_service.classify_intent("Add apples")

    assert intent == VoiceCommandType.UNKNOWN


@pytest.mark.asyncio
async def test_extract_items_error_handling(voice_service, mock_openai_service):
    """Test item extraction with error."""
    mock_openai_service.client.chat.completions.create = AsyncMock(
        side_effect=Exception("API Error")
    )

    items = await voice_service._extract_items_from_text("Add apples")

    assert items == []
