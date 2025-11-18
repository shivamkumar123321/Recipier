"""
Nutrition coaching service with AI-powered personalized advice.

Provides context-aware coaching that:
- Analyzes user's inventory and eating patterns
- Gives proactive suggestions
- Offers motivational guidance
- Recommends recipes based on what user has
"""

import json
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.models.inventory_item import InventoryItem
from app.models.meal import Meal
from app.models.user import User
from app.services.openai_service import OpenAIService, OpenAIServiceError

logger = get_logger(__name__)


class NutritionCoachingService:
    """
    Service for AI-powered nutrition coaching.

    Provides personalized advice based on:
    - User's current inventory
    - Recent eating patterns
    - Health goals
    - Dietary preferences
    """

    # Coaching system prompt
    COACHING_SYSTEM_PROMPT = """You are an expert nutrition coach with a warm, supportive, and motivating personality. Your goal is to help users achieve their health goals through personalized, actionable advice.

**Your Approach:**
- Be encouraging and positive
- Provide specific, actionable recommendations
- Reference the user's actual inventory and context
- Make suggestions feel achievable, not overwhelming
- Celebrate progress and small wins
- Be honest but kind about challenges

**Coaching Principles:**
1. **Context-Aware**: Always reference specific items from their inventory
2. **Practical**: Suggest recipes they can actually make now
3. **Goal-Oriented**: Align advice with their stated health goals
4. **Sustainable**: Focus on long-term habits, not quick fixes
5. **Empowering**: Help them make informed decisions

**Response Format:**
```json
{
  "coaching_message": "Main coaching advice (2-3 paragraphs)",
  "quick_tips": [
    "Tip 1: ...",
    "Tip 2: ...",
    "Tip 3: ..."
  ],
  "recipe_suggestions": [
    {
      "name": "Recipe Name",
      "why": "Why this recipe fits their goals",
      "using_inventory": ["Item 1", "Item 2"]
    }
  ],
  "motivation": "Encouraging closing message"
}
```

**Example:**
"I noticed you have chicken breast and broccoli in your fridge that are expiring in 2 days. Perfect timing for a protein-packed dinner! Here's what I recommend..."

Be conversational, helpful, and genuinely supportive."""

    PROACTIVE_SUGGESTIONS_PROMPT = """Analyze the user's inventory and provide proactive suggestions.

Focus on:
- Items expiring soon (help prevent waste)
- Nutritional gaps (what nutrients might be missing)
- Meal variety (avoid repetition)
- Seasonal eating (when applicable)
- Batch cooking opportunities

**Output Format:**
```json
{
  "urgency": "low|medium|high",
  "primary_suggestion": "Main action to take",
  "reasons": [
    "Reason 1",
    "Reason 2"
  ],
  "action_steps": [
    "Step 1: ...",
    "Step 2: ..."
  ],
  "recipes_to_try": [
    {"name": "...", "uses": ["ingredient1", "ingredient2"]}
  ]
}
```

Be specific and helpful."""

    def __init__(self, openai_service: OpenAIService):
        """
        Initialize nutrition coaching service.

        Args:
            openai_service: OpenAI service instance
        """
        self.openai_service = openai_service

    async def get_personalized_advice(
        self,
        db: AsyncSession,
        user_id: int,
        specific_question: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get personalized nutrition coaching advice.

        Args:
            db: Database session
            user_id: User ID
            specific_question: Optional specific question from user

        Returns:
            Coaching advice dictionary
        """
        logger.info(f"Getting coaching advice for user {user_id}")

        # Gather user context
        context = await self._gather_coaching_context(db, user_id)

        # Build prompt
        if specific_question:
            user_message = f"""The user asks: "{specific_question}"

**User Context:**
{json.dumps(context, indent=2)}

Provide personalized coaching advice that addresses their question while considering their current inventory and goals."""
        else:
            user_message = f"""Provide general nutrition coaching advice for this user.

**User Context:**
{json.dumps(context, indent=2)}

Give personalized, actionable advice based on what they have available and their recent activity."""

        # Get AI coaching
        response = await self.openai_service.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.COACHING_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.8,  # More conversational/warm
            max_tokens=1000,
        )

        content = response.choices[0].message.content
        advice = self.openai_service._parse_json_response(content)

        # Track usage
        if hasattr(response, "usage"):
            self.openai_service._track_usage(response.usage)

        logger.info("Coaching advice generated successfully")
        return advice

    async def get_proactive_suggestions(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> Dict[str, Any]:
        """
        Get proactive suggestions based on inventory analysis.

        Focuses on:
        - Expiring items
        - Nutritional opportunities
        - Meal variety

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Proactive suggestions dictionary
        """
        logger.info(f"Getting proactive suggestions for user {user_id}")

        context = await self._gather_coaching_context(db, user_id)

        # Focus on actionable insights
        user_message = f"""Analyze this user's inventory and provide proactive suggestions.

**Key Information:**
- Items expiring soon: {len(context['expiring_soon'])}
- Total inventory items: {context['total_inventory_items']}
- Recent meals logged: {len(context.get('recent_meals', []))}

**Inventory Details:**
{json.dumps({
    'expiring_soon': context['expiring_soon'][:5],
    'available_inventory': context['available_inventory'][:10]
}, indent=2)}

What should the user prioritize? Be specific and actionable."""

        response = await self.openai_service.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.PROACTIVE_SUGGESTIONS_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=800,
        )

        content = response.choices[0].message.content
        suggestions = self.openai_service._parse_json_response(content)

        # Track usage
        if hasattr(response, "usage"):
            self.openai_service._track_usage(response.usage)

        return suggestions

    async def suggest_recipes_from_inventory(
        self,
        db: AsyncSession,
        user_id: int,
        meal_type: Optional[str] = None,
        max_suggestions: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Suggest recipes based on current inventory.

        "Based on your inventory, you could make..."

        Args:
            db: Database session
            user_id: User ID
            meal_type: Optional meal type filter
            max_suggestions: Maximum number of suggestions

        Returns:
            List of recipe suggestions
        """
        logger.info(
            f"Getting recipe suggestions from inventory for user {user_id}, "
            f"meal_type: {meal_type}"
        )

        # Get inventory
        inventory_query = select(InventoryItem).where(
            InventoryItem.user_id == user_id,
            InventoryItem.deleted_at.is_(None)
        )
        inventory_result = await db.execute(inventory_query)
        inventory_items = inventory_result.scalars().all()

        ingredient_names = [item.name for item in inventory_items[:20]]  # Limit to 20

        if not ingredient_names:
            return []

        # Build prompt
        prompt = f"""Suggest {max_suggestions} recipes that can be made with these ingredients.

**Available Ingredients:**
{', '.join(ingredient_names)}

**Requirements:**
- Meal Type: {meal_type or 'Any'}
- Use as many available ingredients as possible
- Suggest additional ingredients if needed (mark clearly)
- Provide variety

**Output Format:**
```json
[
  {{
    "recipe_name": "...",
    "description": "Brief description",
    "using_from_inventory": ["ingredient1", "ingredient2"],
    "additional_needed": ["ingredient3"],
    "meal_types": ["lunch", "dinner"],
    "prep_time_minutes": 30,
    "why_recommended": "Why this recipe is a good choice"
  }}
]
```

Return a JSON array of {max_suggestions} recipe suggestions."""

        response = await self.openai_service.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            max_tokens=1200,
        )

        content = response.choices[0].message.content
        recipes = self.openai_service._parse_json_response(content)

        # Track usage
        if hasattr(response, "usage"):
            self.openai_service._track_usage(response.usage)

        return recipes if isinstance(recipes, list) else []

    async def _gather_coaching_context(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> Dict[str, Any]:
        """Gather comprehensive context for coaching."""
        # Get inventory
        inventory_query = select(InventoryItem).where(
            InventoryItem.user_id == user_id,
            InventoryItem.deleted_at.is_(None)
        )
        inventory_result = await db.execute(inventory_query)
        inventory_items = inventory_result.scalars().all()

        # Categorize inventory
        available_items = []
        expiring_soon = []
        current_date = date.today()

        for item in inventory_items:
            item_dict = {
                "name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "category": item.category.name if item.category else "other",
            }

            if item.expiration_date:
                days_until_expiry = (item.expiration_date - current_date).days
                if days_until_expiry <= 7:
                    item_dict["days_until_expiry"] = days_until_expiry
                    expiring_soon.append(item_dict)
                else:
                    available_items.append(item_dict)
            else:
                available_items.append(item_dict)

        # Get recent meals (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        meals_query = select(Meal).where(
            Meal.user_id == user_id,
            Meal.meal_date >= week_ago.date(),
            Meal.deleted_at.is_(None)
        ).order_by(Meal.meal_date.desc())
        meals_result = await db.execute(meals_query)
        recent_meals = meals_result.scalars().all()

        recent_meals_data = [
            {
                "name": meal.meal_name,
                "date": meal.meal_date.isoformat(),
                "calories": meal.total_calories,
            }
            for meal in recent_meals[:10]
        ]

        # Get user info
        user_query = select(User).where(User.id == user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one()

        context = {
            "user_id": user_id,
            "available_inventory": available_items[:15],  # Limit for context
            "expiring_soon": expiring_soon,
            "total_inventory_items": len(available_items) + len(expiring_soon),
            "recent_meals": recent_meals_data,
            "user_info": {
                "email": user.email,
                # Add more user profile info as needed
            },
        }

        return context


def get_nutrition_coaching_service() -> NutritionCoachingService:
    """Get or create nutrition coaching service instance."""
    openai_service = OpenAIService(api_key=settings.OPENAI_API_KEY)
    return NutritionCoachingService(openai_service)
