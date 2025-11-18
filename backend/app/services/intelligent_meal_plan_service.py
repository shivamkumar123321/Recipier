"""
Intelligent meal planning service with AI-powered generation.

Uses advanced prompt engineering with chain-of-thought reasoning to:
- Generate personalized meal plans from inventory
- Prioritize expiring ingredients
- Account for dietary restrictions
- Balance nutrition
- Provide recipe recommendations
"""

import hashlib
import json
from datetime import date, datetime, timedelta
from typing import Any, AsyncIterator, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.models.inventory_item import InventoryItem
from app.models.user import User
from app.services.openai_service import OpenAIService, OpenAIServiceError

logger = get_logger(__name__)


class IntelligentMealPlanService:
    """
    Service for AI-powered meal planning with advanced prompt engineering.

    Features:
    - Chain-of-thought prompting for structured planning
    - Inventory-aware meal suggestions
    - Expiring item prioritization
    - Dietary restriction adherence
    - Nutritional balance
    - Redis caching for common patterns
    - Quality checks and validation
    """

    # System prompt with chain-of-thought reasoning
    MEAL_PLANNING_SYSTEM_PROMPT = """You are an expert nutrition coach and meal planning AI assistant. Your goal is to create personalized, practical meal plans that help users achieve their health goals while minimizing food waste.

**Your Approach (Chain-of-Thought):**

1. **Analyze Available Resources**
   - Review user's current inventory
   - Identify items expiring soon (PRIORITIZE THESE)
   - Note dietary restrictions and preferences
   - Consider nutritional goals

2. **Plan Strategically**
   - Use expiring items first (within next 3-7 days)
   - Balance nutrition across meals
   - Ensure variety and appeal
   - Suggest recipes that use inventory items
   - Identify missing ingredients for shopping list

3. **Structure Each Meal**
   - Recipe name and description
   - Ingredients (specify which are from inventory vs. need to buy)
   - Nutritional information (calories, protein, carbs, fat)
   - Preparation time
   - Difficulty level

4. **Quality Checks**
   - Verify all recipes respect dietary restrictions
   - Ensure nutrition targets are met
   - Confirm feasibility with available inventory
   - Balance meal types throughout the day

**Output Format:**
Return a structured JSON meal plan with:
- name: Plan name
- description: Brief overview
- total_days: Number of days
- days: Array of daily meal schedules
- shopping_list: Missing ingredients needed
- nutrition_summary: Aggregate nutrition info
- tips: Helpful coaching advice

**Example Structure:**
```json
{
  "name": "3-Day Balanced Meal Plan",
  "description": "Uses expiring chicken and vegetables, vegetarian-friendly",
  "total_days": 3,
  "days": [
    {
      "day_number": 1,
      "date": "2024-01-15",
      "meals": [
        {
          "meal_type": "breakfast",
          "recipe_name": "Greek Yogurt Parfait",
          "description": "Protein-rich breakfast with berries",
          "ingredients_from_inventory": [
            {"name": "Greek Yogurt", "quantity": 1, "unit": "cup"},
            {"name": "Strawberries", "quantity": 0.5, "unit": "cup", "expiring_soon": true}
          ],
          "ingredients_to_buy": [
            {"name": "Granola", "quantity": 0.25, "unit": "cup"}
          ],
          "nutrition": {
            "calories": 350,
            "protein_g": 20,
            "carbs_g": 45,
            "fat_g": 8
          },
          "prep_time_minutes": 5,
          "difficulty": "easy"
        }
      ],
      "daily_nutrition": {
        "calories": 1800,
        "protein_g": 120,
        "carbs_g": 180,
        "fat_g": 60
      }
    }
  ],
  "shopping_list": [
    {"item": "Granola", "quantity": 1, "unit": "box", "category": "breakfast"},
    {"item": "Olive Oil", "quantity": 1, "unit": "bottle", "category": "pantry"}
  ],
  "nutrition_summary": {
    "avg_daily_calories": 1850,
    "avg_protein_g": 125,
    "avg_carbs_g": 185,
    "avg_fat_g": 62
  },
  "tips": [
    "Use the strawberries expiring in 2 days for breakfast on Day 1",
    "Prep ingredients for Day 2 dinner the night before to save time",
    "The chicken breast from your inventory can be used in 2 different meals"
  ]
}
```

IMPORTANT:
- ALWAYS prioritize ingredients expiring within 3 days
- NEVER suggest recipes with restricted ingredients
- ALWAYS verify ingredient availability
- Include variety - no repetitive meals
- Be practical and achievable"""

    RECIPE_GENERATION_PROMPT = """You are a creative chef and nutrition expert. Generate a custom recipe using the provided ingredients.

**Requirements:**
- Use ingredients from the "available" list
- Respect dietary restrictions
- Suggest additional ingredients if needed (mark as "to_buy")
- Provide clear, step-by-step instructions
- Include accurate nutrition information
- Specify cooking time and difficulty

**Output Format:**
```json
{
  "recipe_name": "...",
  "description": "...",
  "servings": 4,
  "ingredients": [
    {"name": "...", "quantity": 1, "unit": "cup", "from_inventory": true},
    {"name": "...", "quantity": 2, "unit": "tbsp", "from_inventory": false}
  ],
  "instructions": [
    "Step 1: ...",
    "Step 2: ..."
  ],
  "nutrition_per_serving": {
    "calories": 450,
    "protein_g": 30,
    "carbs_g": 40,
    "fat_g": 15
  },
  "prep_time_minutes": 15,
  "cook_time_minutes": 30,
  "difficulty": "medium",
  "cuisine_type": "mediterranean",
  "meal_type": ["lunch", "dinner"]
}
```

Be creative but practical. Ensure the recipe is delicious and nutritionally balanced."""

    def __init__(self, openai_service: OpenAIService):
        """
        Initialize intelligent meal plan service.

        Args:
            openai_service: OpenAI service instance
        """
        self.openai_service = openai_service

    async def generate_meal_plan(
        self,
        db: AsyncSession,
        user_id: int,
        days: int = 3,
        dietary_restrictions: Optional[List[str]] = None,
        target_calories: Optional[int] = None,
        prioritize_expiring: bool = True,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Generate intelligent meal plan using AI with inventory context.

        Args:
            db: Database session
            user_id: User ID
            days: Number of days (3 or 7)
            dietary_restrictions: List of dietary restrictions
            target_calories: Daily calorie target
            prioritize_expiring: Whether to prioritize expiring items
            max_retries: Maximum retry attempts

        Returns:
            Structured meal plan dictionary

        Raises:
            OpenAIServiceError: If generation fails after retries
        """
        logger.info(
            f"Generating {days}-day meal plan for user {user_id}, "
            f"restrictions: {dietary_restrictions}"
        )

        # Check cache first
        cache_key = self._generate_cache_key(
            user_id, days, dietary_restrictions, target_calories
        )
        cached_plan = await self._get_cached_plan(cache_key)
        if cached_plan:
            logger.info("Returning cached meal plan")
            return cached_plan

        # Gather context
        context = await self._gather_planning_context(
            db, user_id, days, dietary_restrictions, target_calories, prioritize_expiring
        )

        # Generate plan with retries
        for attempt in range(max_retries):
            try:
                plan = await self._generate_plan_with_ai(context, attempt)

                # Quality checks
                if self._validate_meal_plan(plan, context):
                    # Cache successful plan
                    await self._cache_plan(cache_key, plan)
                    logger.info(f"Meal plan generated successfully on attempt {attempt + 1}")
                    return plan
                else:
                    logger.warning(f"Plan failed quality check on attempt {attempt + 1}")

            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise OpenAIServiceError(
                        f"Failed to generate meal plan after {max_retries} attempts: {e}"
                    )

        raise OpenAIServiceError("Failed to generate valid meal plan")

    async def _gather_planning_context(
        self,
        db: AsyncSession,
        user_id: int,
        days: int,
        dietary_restrictions: Optional[List[str]],
        target_calories: Optional[int],
        prioritize_expiring: bool,
    ) -> Dict[str, Any]:
        """Gather all context needed for meal planning."""
        # Get user's inventory
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
                "storage_location": item.storage_location,
                "category": item.category.name if item.category else "other",
            }

            if item.expiration_date:
                days_until_expiry = (item.expiration_date - current_date).days
                item_dict["days_until_expiry"] = days_until_expiry

                if days_until_expiry <= 7:
                    item_dict["expiring_soon"] = True
                    expiring_soon.append(item_dict)
                else:
                    available_items.append(item_dict)
            else:
                available_items.append(item_dict)

        # Get user profile for goals
        user_query = select(User).where(User.id == user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one()

        context = {
            "user_id": user_id,
            "days": days,
            "dietary_restrictions": dietary_restrictions or [],
            "target_calories": target_calories,
            "available_inventory": available_items,
            "expiring_soon": expiring_soon,
            "total_inventory_items": len(available_items) + len(expiring_soon),
            "prioritize_expiring": prioritize_expiring,
            "user_goals": {
                # Add user goals if available from user profile
                "goal_type": "maintenance",  # Placeholder
            },
        }

        logger.info(
            f"Context gathered: {len(available_items)} available items, "
            f"{len(expiring_soon)} expiring soon"
        )

        return context

    async def _generate_plan_with_ai(
        self, context: Dict[str, Any], attempt: int
    ) -> Dict[str, Any]:
        """Generate meal plan using AI with context."""
        # Build user message with context
        user_message = f"""Generate a {context['days']}-day meal plan.

**User Context:**
- Dietary Restrictions: {', '.join(context['dietary_restrictions']) if context['dietary_restrictions'] else 'None'}
- Target Calories per Day: {context['target_calories'] or 'Balanced (1800-2000)'}
- Total Inventory Items: {context['total_inventory_items']}

**Ingredients Expiring Soon (USE THESE FIRST):**
{json.dumps(context['expiring_soon'], indent=2) if context['expiring_soon'] else 'None'}

**Available Inventory:**
{json.dumps(context['available_inventory'][:20], indent=2)}  # Limit to first 20 items

**Instructions:**
1. **PRIORITIZE** expiring items in the first 1-2 days
2. Create varied, appealing meals
3. Respect all dietary restrictions
4. Meet the calorie target
5. Minimize food waste
6. Provide a shopping list for missing ingredients

Please generate a complete meal plan following the structure specified in your system prompt."""

        # Call GPT-4 with chain-of-thought prompt
        response = await self.openai_service.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.MEAL_PLANNING_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7 + (attempt * 0.1),  # Increase creativity on retries
            max_tokens=3000,
        )

        content = response.choices[0].message.content
        meal_plan = self.openai_service._parse_json_response(content)

        # Track usage
        if hasattr(response, "usage"):
            self.openai_service._track_usage(response.usage)

        return meal_plan

    def _validate_meal_plan(
        self, plan: Dict[str, Any], context: Dict[str, Any]
    ) -> bool:
        """
        Validate meal plan quality.

        Checks:
        - Has correct number of days
        - Each day has meals
        - Dietary restrictions respected
        - Shopping list present
        """
        try:
            # Check structure
            if "days" not in plan or "shopping_list" not in plan:
                logger.warning("Plan missing required fields")
                return False

            if len(plan["days"]) != context["days"]:
                logger.warning(f"Plan has {len(plan['days'])} days, expected {context['days']}")
                return False

            # Check each day has meals
            for day in plan["days"]:
                if "meals" not in day or len(day["meals"]) == 0:
                    logger.warning(f"Day {day.get('day_number')} has no meals")
                    return False

            # Check dietary restrictions (basic check)
            restricted_ingredients = set(
                r.lower() for r in context.get("dietary_restrictions", [])
            )

            for day in plan["days"]:
                for meal in day["meals"]:
                    for ing_list in ["ingredients_from_inventory", "ingredients_to_buy"]:
                        if ing_list in meal:
                            for ingredient in meal[ing_list]:
                                ing_name = ingredient.get("name", "").lower()
                                for restricted in restricted_ingredients:
                                    if restricted in ing_name:
                                        logger.warning(
                                            f"Restricted ingredient '{ingredient['name']}' "
                                            f"found in meal '{meal['recipe_name']}'"
                                        )
                                        return False

            logger.info("Meal plan passed quality checks")
            return True

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    async def stream_meal_plan_generation(
        self,
        db: AsyncSession,
        user_id: int,
        days: int = 3,
        dietary_restrictions: Optional[List[str]] = None,
        target_calories: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """
        Stream meal plan generation with real-time updates.

        Yields:
            JSON strings with generation progress
        """
        # Gather context
        context = await self._gather_planning_context(
            db, user_id, days, dietary_restrictions, target_calories, True
        )

        # Build prompt
        user_message = f"""Generate a {context['days']}-day meal plan.

Dietary Restrictions: {', '.join(context['dietary_restrictions']) if context['dietary_restrictions'] else 'None'}
Target Calories: {context['target_calories'] or 1800}

Expiring Soon: {json.dumps(context['expiring_soon'][:5])}
Available: {json.dumps(context['available_inventory'][:15])}

Generate complete meal plan with recipes."""

        # Stream response
        stream = await self.openai_service.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.MEAL_PLANNING_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            stream=True,
            temperature=0.7,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def generate_custom_recipe(
        self,
        available_ingredients: List[str],
        dietary_restrictions: Optional[List[str]] = None,
        cuisine_type: Optional[str] = None,
        meal_type: str = "dinner",
    ) -> Dict[str, Any]:
        """
        Generate custom recipe from available ingredients.

        Args:
            available_ingredients: List of ingredient names
            dietary_restrictions: Dietary restrictions to respect
            cuisine_type: Desired cuisine (italian, mexican, etc.)
            meal_type: Meal type (breakfast, lunch, dinner)

        Returns:
            Complete recipe dictionary
        """
        logger.info(
            f"Generating custom recipe: {len(available_ingredients)} ingredients, "
            f"{cuisine_type or 'any'} cuisine, {meal_type}"
        )

        user_message = f"""Create a {meal_type} recipe using these ingredients:

**Available Ingredients:**
{', '.join(available_ingredients)}

**Requirements:**
- Dietary Restrictions: {', '.join(dietary_restrictions) if dietary_restrictions else 'None'}
- Cuisine Type: {cuisine_type or 'Any'}
- Meal Type: {meal_type}

Use as many available ingredients as possible. Suggest additional ingredients if needed.
Provide complete recipe with instructions and nutrition info."""

        response = await self.openai_service.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.RECIPE_GENERATION_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.8,  # More creative for recipes
            max_tokens=1500,
        )

        content = response.choices[0].message.content
        recipe = self.openai_service._parse_json_response(content)

        # Track usage
        if hasattr(response, "usage"):
            self.openai_service._track_usage(response.usage)

        return recipe

    def _generate_cache_key(
        self,
        user_id: int,
        days: int,
        dietary_restrictions: Optional[List[str]],
        target_calories: Optional[int],
    ) -> str:
        """Generate cache key for meal plan."""
        restrictions_str = ",".join(sorted(dietary_restrictions or []))
        key_data = f"mealplan:{user_id}:{days}:{restrictions_str}:{target_calories}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def _get_cached_plan(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached meal plan from Redis."""
        try:
            from app.core.cache import get_redis

            redis = await get_redis()
            cached = await redis.get(f"meal_plan:{cache_key}")
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
        return None

    async def _cache_plan(self, cache_key: str, plan: Dict[str, Any]) -> None:
        """Cache meal plan in Redis."""
        try:
            from app.core.cache import get_redis

            redis = await get_redis()
            ttl = 3600 * 24  # 24 hours
            await redis.setex(
                f"meal_plan:{cache_key}",
                ttl,
                json.dumps(plan),
            )
            logger.info(f"Cached meal plan with key {cache_key}")
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")


def get_intelligent_meal_plan_service() -> IntelligentMealPlanService:
    """Get or create intelligent meal plan service instance."""
    openai_service = OpenAIService(api_key=settings.OPENAI_API_KEY)
    return IntelligentMealPlanService(openai_service)
