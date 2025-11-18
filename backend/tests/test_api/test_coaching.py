"""
Tests for coaching API endpoints.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import AsyncClient


# Sample coaching responses for mocking
SAMPLE_COACHING_ADVICE = {
    "coaching_message": "Great job tracking your food! I noticed you have chicken breast and broccoli expiring in 2 days. This is perfect for a protein-packed dinner tonight!",
    "quick_tips": [
        "Use the chicken and broccoli tonight before they expire",
        "Try meal prepping with your rice for easy lunches",
        "Add more vegetables to boost fiber intake"
    ],
    "recipe_suggestions": [
        {
            "name": "Chicken and Broccoli Stir-Fry",
            "why": "Uses your expiring ingredients and meets your protein goals",
            "using_inventory": ["Chicken Breast", "Broccoli", "Rice"]
        }
    ],
    "motivation": "You're doing great! Keep up the healthy eating habits!"
}

SAMPLE_PROACTIVE_SUGGESTIONS = {
    "urgency": "medium",
    "primary_suggestion": "Cook the chicken breast and broccoli tonight",
    "reasons": [
        "Chicken breast expires in 2 days",
        "Broccoli is starting to wilt",
        "You have all ingredients for a complete meal"
    ],
    "action_steps": [
        "Marinate the chicken for 30 minutes",
        "Steam the broccoli while chicken cooks",
        "Serve over rice from your pantry"
    ],
    "recipes_to_try": [
        {"name": "Garlic Chicken with Broccoli", "uses": ["chicken", "broccoli", "garlic"]}
    ]
}

SAMPLE_RECIPE_SUGGESTIONS = [
    {
        "recipe_name": "Chicken Fried Rice",
        "description": "Quick and delicious fried rice with chicken and vegetables",
        "using_from_inventory": ["Chicken Breast", "Rice", "Eggs", "Soy Sauce"],
        "additional_needed": ["Green Onions"],
        "meal_types": ["lunch", "dinner"],
        "prep_time_minutes": 15,
        "why_recommended": "Uses your chicken before it expires and makes good use of leftover rice"
    },
    {
        "recipe_name": "Chicken and Vegetable Stir-Fry",
        "description": "Healthy stir-fry packed with protein and vegetables",
        "using_from_inventory": ["Chicken Breast", "Broccoli", "Carrots"],
        "additional_needed": ["Sesame Oil"],
        "meal_types": ["dinner"],
        "prep_time_minutes": 20,
        "why_recommended": "Great way to use expiring vegetables"
    }
]

SAMPLE_CUSTOM_RECIPE = {
    "recipe_name": "Lemon Herb Chicken with Roasted Vegetables",
    "description": "Juicy chicken breast with colorful roasted vegetables",
    "servings": 4,
    "ingredients": [
        {"name": "Chicken Breast", "quantity": 4, "unit": "pieces", "from_inventory": True},
        {"name": "Broccoli", "quantity": 2, "unit": "cups", "from_inventory": True},
        {"name": "Olive Oil", "quantity": 2, "unit": "tbsp", "from_inventory": False},
        {"name": "Lemon", "quantity": 1, "unit": "whole", "from_inventory": False}
    ],
    "instructions": [
        "Preheat oven to 425°F",
        "Season chicken with herbs, salt, and pepper",
        "Toss vegetables with olive oil",
        "Roast chicken and vegetables for 25 minutes",
        "Squeeze lemon over chicken before serving"
    ],
    "nutrition_per_serving": {
        "calories": 350,
        "protein_g": 35,
        "carbs_g": 15,
        "fat_g": 12
    },
    "prep_time_minutes": 10,
    "cook_time_minutes": 25,
    "difficulty": "easy",
    "cuisine_type": "mediterranean",
    "meal_type": ["lunch", "dinner"]
}


@pytest.mark.asyncio
async def test_get_coaching_advice_success(
    client: AsyncClient,
    verified_auth_headers: dict,
    db,
):
    """Test getting personalized coaching advice."""
    with patch("app.api.v1.coaching.get_nutrition_coaching_service") as mock_service:
        # Mock coaching service
        mock_coach = Mock()
        mock_coach.get_personalized_advice = AsyncMock(
            return_value=SAMPLE_COACHING_ADVICE
        )
        mock_service.return_value = mock_coach

        response = await client.post(
            "/api/v1/coaching/advice",
            headers=verified_auth_headers,
            json={},
        )

        assert response.status_code == 200
        data = response.json()
        assert "coaching_message" in data
        assert "quick_tips" in data
        assert len(data["quick_tips"]) == 3
        assert "recipe_suggestions" in data
        assert "motivation" in data


@pytest.mark.asyncio
async def test_get_coaching_advice_with_question(
    client: AsyncClient,
    verified_auth_headers: dict,
    db,
):
    """Test getting coaching advice with specific question."""
    with patch("app.api.v1.coaching.get_nutrition_coaching_service") as mock_service:
        mock_coach = Mock()
        mock_coach.get_personalized_advice = AsyncMock(
            return_value=SAMPLE_COACHING_ADVICE
        )
        mock_service.return_value = mock_coach

        response = await client.post(
            "/api/v1/coaching/advice",
            headers=verified_auth_headers,
            json={
                "specific_question": "What should I cook for dinner tonight?"
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "coaching_message" in data

        # Verify service was called with the question
        mock_coach.get_personalized_advice.assert_called_once()
        call_args = mock_coach.get_personalized_advice.call_args
        assert call_args[1]["specific_question"] == "What should I cook for dinner tonight?"


@pytest.mark.asyncio
async def test_get_proactive_suggestions_success(
    client: AsyncClient,
    verified_auth_headers: dict,
    db,
):
    """Test getting proactive suggestions."""
    with patch("app.api.v1.coaching.get_nutrition_coaching_service") as mock_service:
        mock_coach = Mock()
        mock_coach.get_proactive_suggestions = AsyncMock(
            return_value=SAMPLE_PROACTIVE_SUGGESTIONS
        )
        mock_service.return_value = mock_coach

        response = await client.post(
            "/api/v1/coaching/suggestions",
            headers=verified_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["urgency"] in ["low", "medium", "high"]
        assert data["urgency"] == "medium"
        assert "primary_suggestion" in data
        assert "reasons" in data
        assert len(data["reasons"]) > 0
        assert "action_steps" in data
        assert "recipes_to_try" in data


@pytest.mark.asyncio
async def test_get_recipes_from_inventory_success(
    client: AsyncClient,
    verified_auth_headers: dict,
    db,
):
    """Test getting recipe suggestions from inventory."""
    with patch("app.api.v1.coaching.get_nutrition_coaching_service") as mock_service:
        mock_coach = Mock()
        mock_coach.suggest_recipes_from_inventory = AsyncMock(
            return_value=SAMPLE_RECIPE_SUGGESTIONS
        )
        mock_service.return_value = mock_coach

        response = await client.post(
            "/api/v1/coaching/recipes-from-inventory",
            headers=verified_auth_headers,
            json={
                "meal_type": "dinner",
                "max_suggestions": 3
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "recipes" in data
        assert len(data["recipes"]) == 2
        assert data["recipes"][0]["recipe_name"] == "Chicken Fried Rice"
        assert "using_from_inventory" in data["recipes"][0]
        assert "additional_needed" in data["recipes"][0]
        assert "message" in data


@pytest.mark.asyncio
async def test_get_recipes_from_inventory_no_meal_type(
    client: AsyncClient,
    verified_auth_headers: dict,
    db,
):
    """Test getting recipes without meal type filter."""
    with patch("app.api.v1.coaching.get_nutrition_coaching_service") as mock_service:
        mock_coach = Mock()
        mock_coach.suggest_recipes_from_inventory = AsyncMock(
            return_value=SAMPLE_RECIPE_SUGGESTIONS
        )
        mock_service.return_value = mock_coach

        response = await client.post(
            "/api/v1/coaching/recipes-from-inventory",
            headers=verified_auth_headers,
            json={
                "max_suggestions": 5
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "recipes" in data


@pytest.mark.asyncio
async def test_get_recipes_from_inventory_empty(
    client: AsyncClient,
    verified_auth_headers: dict,
    db,
):
    """Test getting recipes with empty inventory."""
    with patch("app.api.v1.coaching.get_nutrition_coaching_service") as mock_service:
        mock_coach = Mock()
        mock_coach.suggest_recipes_from_inventory = AsyncMock(return_value=[])
        mock_service.return_value = mock_coach

        response = await client.post(
            "/api/v1/coaching/recipes-from-inventory",
            headers=verified_auth_headers,
            json={},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["recipes"]) == 0
        assert "enough ingredients" in data["message"].lower()


@pytest.mark.asyncio
async def test_generate_custom_recipe_success(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test generating custom recipe."""
    with patch("app.api.v1.coaching.get_intelligent_meal_plan_service") as mock_service:
        mock_planner = Mock()
        mock_planner.generate_custom_recipe = AsyncMock(
            return_value=SAMPLE_CUSTOM_RECIPE
        )
        mock_service.return_value = mock_planner

        response = await client.post(
            "/api/v1/coaching/generate-recipe",
            headers=verified_auth_headers,
            json={
                "available_ingredients": ["Chicken Breast", "Broccoli", "Garlic"],
                "dietary_restrictions": ["gluten-free"],
                "cuisine_type": "mediterranean",
                "meal_type": "dinner"
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["recipe_name"] == "Lemon Herb Chicken with Roasted Vegetables"
        assert "ingredients" in data
        assert "instructions" in data
        assert len(data["instructions"]) == 5
        assert "nutrition_per_serving" in data
        assert data["nutrition_per_serving"]["calories"] == 350
        assert data["prep_time_minutes"] == 10
        assert data["cook_time_minutes"] == 25
        assert data["difficulty"] == "easy"


@pytest.mark.asyncio
async def test_generate_custom_recipe_minimal_params(
    client: AsyncClient,
    verified_auth_headers: dict,
):
    """Test generating custom recipe with minimal params."""
    with patch("app.api.v1.coaching.get_intelligent_meal_plan_service") as mock_service:
        mock_planner = Mock()
        mock_planner.generate_custom_recipe = AsyncMock(
            return_value=SAMPLE_CUSTOM_RECIPE
        )
        mock_service.return_value = mock_planner

        response = await client.post(
            "/api/v1/coaching/generate-recipe",
            headers=verified_auth_headers,
            json={
                "available_ingredients": ["Chicken", "Rice"]
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "recipe_name" in data


@pytest.mark.asyncio
async def test_coaching_advice_unauthorized(
    client: AsyncClient,
):
    """Test coaching advice without authentication."""
    response = await client.post(
        "/api/v1/coaching/advice",
        json={},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_coaching_ai_service_error(
    client: AsyncClient,
    verified_auth_headers: dict,
    db,
):
    """Test coaching advice with AI service error."""
    with patch("app.api.v1.coaching.get_nutrition_coaching_service") as mock_service:
        from app.services.openai_service import OpenAIServiceError

        mock_coach = Mock()
        mock_coach.get_personalized_advice = AsyncMock(
            side_effect=OpenAIServiceError("AI service error")
        )
        mock_service.return_value = mock_coach

        response = await client.post(
            "/api/v1/coaching/advice",
            headers=verified_auth_headers,
            json={},
        )

        assert response.status_code == 502
        assert "AI service error" in response.json()["detail"]
