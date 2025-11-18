"""
Voice command processing service.

Handles voice command interpretation with prompt engineering for:
- Adding inventory items
- Querying inventory ("What can I cook with...")
- Checking expiration dates
- General inventory questions
"""

import json
import re
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.services.inventory_service import inventory_service
from app.services.openai_service import OpenAIService, OpenAIServiceError

logger = get_logger(__name__)


class VoiceCommandType(str, Enum):
    """Types of voice commands supported."""

    ADD_ITEMS = "add_items"
    QUERY_RECIPES = "query_recipes"
    CHECK_EXPIRATION = "check_expiration"
    SEARCH_INVENTORY = "search_inventory"
    UNKNOWN = "unknown"


class VoiceCommandResult:
    """Result of voice command processing."""

    def __init__(
        self,
        command_type: VoiceCommandType,
        success: bool,
        data: Any = None,
        message: str = "",
        error: Optional[str] = None,
    ):
        self.command_type = command_type
        self.success = success
        self.data = data
        self.message = message
        self.error = error


class VoiceCommandService:
    """
    Service for processing voice commands with AI.

    Uses prompt engineering to interpret various voice commands and execute
    appropriate actions on the inventory system.
    """

    # System prompts for different command types
    INTENT_CLASSIFICATION_PROMPT = """You are a smart food inventory assistant. Analyze the user's voice command and classify the intent.

Available intents:
- add_items: User wants to add items to inventory (e.g., "Add 3 apples", "I bought chicken and rice")
- query_recipes: User wants recipe suggestions (e.g., "What can I cook with chicken and rice?")
- check_expiration: User asks about expiration dates (e.g., "When does my milk expire?", "What's expiring soon?")
- search_inventory: User wants to search/list items (e.g., "What do I have?", "Show me all vegetables")
- unknown: Cannot determine intent

Respond with ONLY the intent name, nothing else."""

    ADD_ITEMS_PROMPT = """You are a food inventory assistant. Extract food items with quantities from the user's text.

Instructions:
- Extract item name, quantity, unit
- Infer storage location (pantry, fridge, freezer) based on item type
- Infer food category (protein, vegetable, fruit, dairy, grain, etc.)
- If no quantity specified, use 1 as default
- If no unit specified, use "item" or infer appropriate unit (lb, oz, cup, etc.)
- Handle common phrases like "a bag of", "some", "a few"

Examples:
Input: "Add 3 apples and 2 pounds of chicken"
Output: [
  {"name": "Apple", "quantity": 3, "unit": "items", "storage_location": "pantry", "category": "fruit"},
  {"name": "Chicken", "quantity": 2, "unit": "lbs", "storage_location": "fridge", "category": "protein"}
]

Input: "I bought milk, eggs, and a bag of rice"
Output: [
  {"name": "Milk", "quantity": 1, "unit": "gallon", "storage_location": "fridge", "category": "dairy"},
  {"name": "Eggs", "quantity": 12, "unit": "items", "storage_location": "fridge", "category": "protein"},
  {"name": "Rice", "quantity": 1, "unit": "bag", "storage_location": "pantry", "category": "grain"}
]

Input: "Got some broccoli and frozen pizza"
Output: [
  {"name": "Broccoli", "quantity": 1, "unit": "bunch", "storage_location": "fridge", "category": "vegetable"},
  {"name": "Frozen Pizza", "quantity": 1, "unit": "item", "storage_location": "freezer", "category": "prepared"}
]

Respond ONLY with valid JSON array, no markdown or explanation."""

    RECIPE_QUERY_PROMPT = """You are a helpful cooking assistant. Extract the ingredients the user wants to use for cooking.

Instructions:
- Extract ingredient names mentioned in the query
- Return as simple list of ingredient names
- Clean up plurals and variations (e.g., "chickens" -> "chicken")

Examples:
Input: "What can I cook with chicken and rice?"
Output: ["chicken", "rice"]

Input: "I have tomatoes, onions, and garlic. What can I make?"
Output: ["tomatoes", "onions", "garlic"]

Input: "Recipe ideas with leftover pasta"
Output: ["pasta"]

Respond ONLY with valid JSON array of ingredient names."""

    EXPIRATION_QUERY_PROMPT = """You are a food inventory assistant helping check expiration dates.

Extract:
- Item name (if specified)
- Time window (if specified, e.g., "within 3 days", "this week", "today")

Examples:
Input: "When does my milk expire?"
Output: {"item": "milk", "days": null}

Input: "What's expiring within 3 days?"
Output: {"item": null, "days": 3}

Input: "Show me items expiring soon"
Output: {"item": null, "days": 7}

Input: "Is my chicken still good?"
Output: {"item": "chicken", "days": null}

Respond ONLY with valid JSON object."""

    def __init__(self, openai_service: OpenAIService):
        """
        Initialize voice command service.

        Args:
            openai_service: OpenAI service instance
        """
        self.openai_service = openai_service

    async def classify_intent(self, text: str) -> VoiceCommandType:
        """
        Classify the intent of a voice command.

        Args:
            text: Transcribed text from user

        Returns:
            VoiceCommandType enum value
        """
        try:
            # Use GPT to classify intent
            response = await self.openai_service.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use faster model for intent classification
                messages=[
                    {"role": "system", "content": self.INTENT_CLASSIFICATION_PROMPT},
                    {"role": "user", "content": text},
                ],
                temperature=0.3,
                max_tokens=50,
            )

            intent = response.choices[0].message.content.strip().lower()

            # Map to enum
            intent_map = {
                "add_items": VoiceCommandType.ADD_ITEMS,
                "query_recipes": VoiceCommandType.QUERY_RECIPES,
                "check_expiration": VoiceCommandType.CHECK_EXPIRATION,
                "search_inventory": VoiceCommandType.SEARCH_INVENTORY,
            }

            return intent_map.get(intent, VoiceCommandType.UNKNOWN)

        except Exception as e:
            logger.error(f"Failed to classify intent: {e}")
            return VoiceCommandType.UNKNOWN

    async def process_add_items_command(
        self, text: str, db: AsyncSession, user_id: int
    ) -> VoiceCommandResult:
        """
        Process a command to add items to inventory.

        Args:
            text: Transcribed text
            db: Database session
            user_id: User ID

        Returns:
            VoiceCommandResult with added items
        """
        try:
            # Extract items using GPT
            items_data = await self._extract_items_from_text(text)

            if not items_data:
                return VoiceCommandResult(
                    command_type=VoiceCommandType.ADD_ITEMS,
                    success=False,
                    message="No items could be extracted from your command.",
                )

            # Add each item to inventory
            added_items = []
            for item_data in items_data:
                try:
                    # Create inventory item
                    from app.schemas.inventory import InventoryItemCreate

                    item_create = InventoryItemCreate(
                        name=item_data["name"],
                        quantity=item_data.get("quantity", 1),
                        unit=item_data.get("unit", "item"),
                        storage_location=item_data.get("storage_location"),
                    )

                    item = await inventory_service.create_item(
                        db=db, item_data=item_create, user_id=user_id
                    )
                    added_items.append(item)

                except Exception as e:
                    logger.warning(f"Failed to add item {item_data.get('name')}: {e}")
                    continue

            await db.commit()

            if not added_items:
                return VoiceCommandResult(
                    command_type=VoiceCommandType.ADD_ITEMS,
                    success=False,
                    message="Failed to add any items to inventory.",
                )

            return VoiceCommandResult(
                command_type=VoiceCommandType.ADD_ITEMS,
                success=True,
                data={"items": added_items},
                message=f"Successfully added {len(added_items)} item(s) to your inventory.",
            )

        except Exception as e:
            logger.error(f"Failed to process add items command: {e}")
            return VoiceCommandResult(
                command_type=VoiceCommandType.ADD_ITEMS,
                success=False,
                error=str(e),
                message="Failed to process your command.",
            )

    async def process_recipe_query_command(
        self, text: str, db: AsyncSession, user_id: int
    ) -> VoiceCommandResult:
        """
        Process a command to query recipes.

        Args:
            text: Transcribed text
            db: Database session
            user_id: User ID

        Returns:
            VoiceCommandResult with recipe suggestions
        """
        try:
            # Extract ingredients from query
            ingredients = await self._extract_recipe_ingredients(text)

            if not ingredients:
                return VoiceCommandResult(
                    command_type=VoiceCommandType.QUERY_RECIPES,
                    success=False,
                    message="I couldn't identify any ingredients in your query.",
                )

            # Get recipe suggestions from OpenAI
            recipes = await self.openai_service.suggest_recipes(
                ingredients=ingredients, max_results=5
            )

            if not recipes:
                return VoiceCommandResult(
                    command_type=VoiceCommandType.QUERY_RECIPES,
                    success=False,
                    message=f"I couldn't find any recipes using {', '.join(ingredients)}.",
                )

            return VoiceCommandResult(
                command_type=VoiceCommandType.QUERY_RECIPES,
                success=True,
                data={"ingredients": ingredients, "recipes": recipes},
                message=f"Found {len(recipes)} recipe(s) using {', '.join(ingredients)}.",
            )

        except Exception as e:
            logger.error(f"Failed to process recipe query: {e}")
            return VoiceCommandResult(
                command_type=VoiceCommandType.QUERY_RECIPES,
                success=False,
                error=str(e),
                message="Failed to find recipes.",
            )

    async def process_expiration_check_command(
        self, text: str, db: AsyncSession, user_id: int
    ) -> VoiceCommandResult:
        """
        Process a command to check expiration dates.

        Args:
            text: Transcribed text
            db: Database session
            user_id: User ID

        Returns:
            VoiceCommandResult with expiration information
        """
        try:
            # Extract query parameters
            query_params = await self._extract_expiration_query(text)
            item_name = query_params.get("item")
            days = query_params.get("days", 7)  # Default to 7 days

            if item_name:
                # Search for specific item
                items, _ = await inventory_service.get_user_inventory(
                    db=db, user_id=user_id, search=item_name, limit=10
                )

                if not items:
                    return VoiceCommandResult(
                        command_type=VoiceCommandType.CHECK_EXPIRATION,
                        success=False,
                        message=f"I couldn't find '{item_name}' in your inventory.",
                    )

                # Filter items with expiration dates
                items_with_expiration = [
                    item for item in items if item.expiration_date is not None
                ]

                if not items_with_expiration:
                    return VoiceCommandResult(
                        command_type=VoiceCommandType.CHECK_EXPIRATION,
                        success=True,
                        data={"items": items},
                        message=f"Found {item_name}, but no expiration date is set.",
                    )

                return VoiceCommandResult(
                    command_type=VoiceCommandType.CHECK_EXPIRATION,
                    success=True,
                    data={"items": items_with_expiration},
                    message=f"Found {len(items_with_expiration)} item(s) matching '{item_name}'.",
                )

            else:
                # Get items expiring within specified days
                items, total = await inventory_service.get_expiring_items(
                    db=db, user_id=user_id, days=days, limit=100
                )

                if not items:
                    return VoiceCommandResult(
                        command_type=VoiceCommandType.CHECK_EXPIRATION,
                        success=True,
                        data={"items": [], "days": days},
                        message=f"No items are expiring within the next {days} day(s).",
                    )

                return VoiceCommandResult(
                    command_type=VoiceCommandType.CHECK_EXPIRATION,
                    success=True,
                    data={"items": items, "days": days},
                    message=f"Found {len(items)} item(s) expiring within {days} day(s).",
                )

        except Exception as e:
            logger.error(f"Failed to process expiration check: {e}")
            return VoiceCommandResult(
                command_type=VoiceCommandType.CHECK_EXPIRATION,
                success=False,
                error=str(e),
                message="Failed to check expiration dates.",
            )

    async def process_search_inventory_command(
        self, text: str, db: AsyncSession, user_id: int
    ) -> VoiceCommandResult:
        """
        Process a command to search/list inventory items.

        Args:
            text: Transcribed text
            db: Database session
            user_id: User ID

        Returns:
            VoiceCommandResult with search results
        """
        try:
            # Extract search query (look for keywords like vegetables, fruits, etc.)
            search_query = self._extract_search_query(text)

            items, total = await inventory_service.get_user_inventory(
                db=db, user_id=user_id, search=search_query, limit=100
            )

            if not items:
                message = (
                    f"No items found matching '{search_query}'."
                    if search_query
                    else "Your inventory is empty."
                )
                return VoiceCommandResult(
                    command_type=VoiceCommandType.SEARCH_INVENTORY,
                    success=True,
                    data={"items": [], "query": search_query},
                    message=message,
                )

            message = (
                f"Found {len(items)} item(s) matching '{search_query}'."
                if search_query
                else f"You have {len(items)} item(s) in your inventory."
            )

            return VoiceCommandResult(
                command_type=VoiceCommandType.SEARCH_INVENTORY,
                success=True,
                data={"items": items, "query": search_query, "total": total},
                message=message,
            )

        except Exception as e:
            logger.error(f"Failed to process search command: {e}")
            return VoiceCommandResult(
                command_type=VoiceCommandType.SEARCH_INVENTORY,
                success=False,
                error=str(e),
                message="Failed to search inventory.",
            )

    async def process_voice_command(
        self, transcribed_text: str, db: AsyncSession, user_id: int
    ) -> VoiceCommandResult:
        """
        Process a voice command by classifying intent and executing action.

        Args:
            transcribed_text: Text transcribed from voice
            db: Database session
            user_id: User ID

        Returns:
            VoiceCommandResult with execution results
        """
        logger.info(f"Processing voice command: {transcribed_text}")

        # Classify intent
        intent = await self.classify_intent(transcribed_text)
        logger.info(f"Classified intent: {intent}")

        # Route to appropriate handler
        if intent == VoiceCommandType.ADD_ITEMS:
            return await self.process_add_items_command(transcribed_text, db, user_id)

        elif intent == VoiceCommandType.QUERY_RECIPES:
            return await self.process_recipe_query_command(
                transcribed_text, db, user_id
            )

        elif intent == VoiceCommandType.CHECK_EXPIRATION:
            return await self.process_expiration_check_command(
                transcribed_text, db, user_id
            )

        elif intent == VoiceCommandType.SEARCH_INVENTORY:
            return await self.process_search_inventory_command(
                transcribed_text, db, user_id
            )

        else:
            return VoiceCommandResult(
                command_type=VoiceCommandType.UNKNOWN,
                success=False,
                message="I didn't understand that command. Try saying something like 'Add 3 apples' or 'What can I cook with chicken?'",
            )

    # Helper methods for extracting data

    async def _extract_items_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract inventory items from text using GPT."""
        try:
            response = await self.openai_service.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.ADD_ITEMS_PROMPT},
                    {"role": "user", "content": text},
                ],
                temperature=0.3,
                max_tokens=500,
            )

            content = response.choices[0].message.content.strip()
            items = self.openai_service._parse_json_response(content)

            return items if isinstance(items, list) else []

        except Exception as e:
            logger.error(f"Failed to extract items: {e}")
            return []

    async def _extract_recipe_ingredients(self, text: str) -> List[str]:
        """Extract ingredients from recipe query."""
        try:
            response = await self.openai_service.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.RECIPE_QUERY_PROMPT},
                    {"role": "user", "content": text},
                ],
                temperature=0.3,
                max_tokens=200,
            )

            content = response.choices[0].message.content.strip()
            ingredients = self.openai_service._parse_json_response(content)

            return ingredients if isinstance(ingredients, list) else []

        except Exception as e:
            logger.error(f"Failed to extract ingredients: {e}")
            return []

    async def _extract_expiration_query(self, text: str) -> Dict[str, Any]:
        """Extract expiration query parameters."""
        try:
            response = await self.openai_service.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.EXPIRATION_QUERY_PROMPT},
                    {"role": "user", "content": text},
                ],
                temperature=0.3,
                max_tokens=100,
            )

            content = response.choices[0].message.content.strip()
            query_params = self.openai_service._parse_json_response(content)

            return query_params if isinstance(query_params, dict) else {}

        except Exception as e:
            logger.error(f"Failed to extract expiration query: {e}")
            return {}

    def _extract_search_query(self, text: str) -> Optional[str]:
        """Extract search query from text using simple pattern matching."""
        # Look for patterns like "show me X", "what X do I have", "list all X"
        patterns = [
            r"show\s+(?:me\s+)?(?:all\s+)?(.+)",
            r"what\s+(.+?)\s+do\s+I\s+have",
            r"list\s+(?:all\s+)?(.+)",
            r"do\s+I\s+have\s+(?:any\s+)?(.+)",
        ]

        text_lower = text.lower()

        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                query = match.group(1).strip()
                # Clean up common words
                query = re.sub(r"\b(items?|things?|in\s+my\s+inventory)\b", "", query).strip()
                return query if query else None

        return None


# Create singleton instance
voice_command_service: Optional[VoiceCommandService] = None


def get_voice_command_service() -> VoiceCommandService:
    """Get or create voice command service instance."""
    global voice_command_service

    if voice_command_service is None:
        from app.core.config import settings

        openai_service = OpenAIService(api_key=settings.OPENAI_API_KEY)
        voice_command_service = VoiceCommandService(openai_service)

    return voice_command_service
