"""
Nutrition coaching API endpoints.

Provides:
- Personalized coaching advice
- Proactive suggestions based on inventory
- Recipe recommendations from available ingredients
- Custom recipe generation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.logging import get_logger
from app.models.user import User
from app.schemas.coaching import (
    CoachingAdviceRequest,
    CoachingAdviceResponse,
    CustomRecipeGenerateRequest,
    CustomRecipeResponse,
    ProactiveSuggestionsResponse,
    RecipeFromInventoryRequest,
    RecipeFromInventoryResponse,
    RecipeSuggestionFromInventory,
)
from app.services.intelligent_meal_plan_service import (
    get_intelligent_meal_plan_service,
)
from app.services.nutrition_coaching_service import get_nutrition_coaching_service
from app.services.openai_service import OpenAIServiceError

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/advice",
    response_model=CoachingAdviceResponse,
    summary="Get personalized nutrition advice",
    description="Get AI-powered coaching advice based on inventory and goals",
)
async def get_coaching_advice(
    request: CoachingAdviceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> CoachingAdviceResponse:
    """
    Get personalized nutrition coaching advice.

    The AI coach analyzes:
    - Your current inventory
    - Items expiring soon
    - Recent eating patterns
    - Health goals

    And provides:
    - Personalized coaching message
    - Quick actionable tips
    - Recipe suggestions using your inventory
    - Motivational guidance

    Args:
        request: Coaching advice request (optional specific question)
        db: Database session
        current_user: Current authenticated user

    Returns:
        Personalized coaching advice

    Raises:
        HTTPException: If advice generation fails
    """
    logger.info(
        f"Coaching advice request from user {current_user.id}, "
        f"question: {request.specific_question or 'general'}"
    )

    try:
        coaching_service = get_nutrition_coaching_service()

        advice = await coaching_service.get_personalized_advice(
            db=db,
            user_id=current_user.id,
            specific_question=request.specific_question,
        )

        logger.info(f"Coaching advice generated for user {current_user.id}")

        return CoachingAdviceResponse(**advice)

    except OpenAIServiceError as e:
        logger.error(f"OpenAI service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Coaching advice generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate coaching advice",
        )


@router.post(
    "/suggestions",
    response_model=ProactiveSuggestionsResponse,
    summary="Get proactive suggestions",
    description="Get AI-powered proactive suggestions based on inventory analysis",
)
async def get_proactive_suggestions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProactiveSuggestionsResponse:
    """
    Get proactive suggestions based on inventory.

    The AI analyzes your inventory and provides:
    - Urgency level (low/medium/high)
    - Primary action to take
    - Reasons for the suggestion
    - Specific action steps
    - Recipe recommendations

    Great for:
    - "What should I cook today?"
    - Preventing food waste
    - Meal planning inspiration

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Proactive suggestions

    Raises:
        HTTPException: If suggestion generation fails
    """
    logger.info(f"Proactive suggestions request from user {current_user.id}")

    try:
        coaching_service = get_nutrition_coaching_service()

        suggestions = await coaching_service.get_proactive_suggestions(
            db=db,
            user_id=current_user.id,
        )

        logger.info(
            f"Proactive suggestions generated for user {current_user.id}, "
            f"urgency: {suggestions.get('urgency')}"
        )

        return ProactiveSuggestionsResponse(**suggestions)

    except OpenAIServiceError as e:
        logger.error(f"OpenAI service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Suggestion generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate suggestions",
        )


@router.post(
    "/recipes-from-inventory",
    response_model=RecipeFromInventoryResponse,
    summary="Get recipe suggestions from inventory",
    description="Get AI-powered recipe suggestions using your available ingredients",
)
async def get_recipes_from_inventory(
    request: RecipeFromInventoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RecipeFromInventoryResponse:
    """
    Get recipe suggestions based on your current inventory.

    "Based on your inventory, you could make..."

    The AI:
    - Analyzes your available ingredients
    - Suggests creative recipes
    - Tells you what additional ingredients you might need
    - Explains why each recipe is recommended

    Perfect for:
    - "What can I make with what I have?"
    - Using up ingredients before they expire
    - Meal inspiration

    Args:
        request: Recipe request (optional meal type filter)
        db: Database session
        current_user: Current authenticated user

    Returns:
        Recipe suggestions from inventory

    Raises:
        HTTPException: If recipe generation fails
    """
    logger.info(
        f"Recipe from inventory request from user {current_user.id}, "
        f"meal_type: {request.meal_type}, max: {request.max_suggestions}"
    )

    try:
        coaching_service = get_nutrition_coaching_service()

        recipes = await coaching_service.suggest_recipes_from_inventory(
            db=db,
            user_id=current_user.id,
            meal_type=request.meal_type,
            max_suggestions=request.max_suggestions,
        )

        if not recipes:
            return RecipeFromInventoryResponse(
                recipes=[],
                total_inventory_items=0,
                message="You don't have enough ingredients in your inventory yet. Add some items to get recipe suggestions!",
            )

        recipe_objects = [
            RecipeSuggestionFromInventory(**recipe) for recipe in recipes
        ]

        logger.info(f"Generated {len(recipes)} recipe suggestions for user {current_user.id}")

        return RecipeFromInventoryResponse(
            recipes=recipe_objects,
            total_inventory_items=len(recipes),  # Placeholder
            message=f"Found {len(recipes)} recipe(s) you can make with your ingredients!",
        )

    except OpenAIServiceError as e:
        logger.error(f"OpenAI service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Recipe generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recipe suggestions",
        )


@router.post(
    "/generate-recipe",
    response_model=CustomRecipeResponse,
    summary="Generate custom recipe",
    description="Generate a custom recipe from specific ingredients",
)
async def generate_custom_recipe(
    request: CustomRecipeGenerateRequest,
    current_user: User = Depends(get_current_active_user),
) -> CustomRecipeResponse:
    """
    Generate a custom recipe from specific ingredients.

    The AI creates a complete recipe with:
    - Step-by-step instructions
    - Nutrition information per serving
    - Cooking times and difficulty
    - Suggestions for additional ingredients

    Args:
        request: Custom recipe request with ingredients and preferences
        current_user: Current authenticated user

    Returns:
        Complete custom recipe

    Raises:
        HTTPException: If recipe generation fails
    """
    logger.info(
        f"Custom recipe generation request from user {current_user.id}, "
        f"ingredients: {len(request.available_ingredients)}, "
        f"cuisine: {request.cuisine_type}, meal: {request.meal_type}"
    )

    try:
        meal_plan_service = get_intelligent_meal_plan_service()

        recipe = await meal_plan_service.generate_custom_recipe(
            available_ingredients=request.available_ingredients,
            dietary_restrictions=request.dietary_restrictions,
            cuisine_type=request.cuisine_type,
            meal_type=request.meal_type,
        )

        logger.info(
            f"Custom recipe '{recipe.get('recipe_name')}' generated for user {current_user.id}"
        )

        return CustomRecipeResponse(**recipe)

    except OpenAIServiceError as e:
        logger.error(f"OpenAI service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Recipe generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate custom recipe",
        )
