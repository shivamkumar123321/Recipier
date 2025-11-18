"""
Voice cooking assistant service with real-time audio processing.

Provides capabilities for:
- Real-time voice transcription (Whisper)
- Intelligent cooking assistance (GPT-4)
- Text-to-speech responses (OpenAI TTS)
- Timer management
- Unit conversion
- Ingredient substitution suggestions
- Step-by-step recipe guidance
"""

import asyncio
import io
import json
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.core.logging import get_logger
from app.services.openai_service import OpenAIService, OpenAIServiceError, get_openai_service

logger = get_logger(__name__)


class Timer:
    """Represents an active cooking timer."""

    def __init__(self, duration_seconds: int, label: str = "Timer"):
        self.duration_seconds = duration_seconds
        self.label = label
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(seconds=duration_seconds)
        self.is_active = True

    def time_remaining(self) -> int:
        """Get remaining time in seconds."""
        if not self.is_active:
            return 0

        remaining = (self.end_time - datetime.now()).total_seconds()
        return max(0, int(remaining))

    def is_finished(self) -> bool:
        """Check if timer has finished."""
        return self.time_remaining() <= 0

    def cancel(self):
        """Cancel the timer."""
        self.is_active = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert timer to dictionary."""
        return {
            "label": self.label,
            "duration_seconds": self.duration_seconds,
            "time_remaining_seconds": self.time_remaining(),
            "is_active": self.is_active,
            "is_finished": self.is_finished(),
        }


class ConversationContext:
    """Manages conversation context for voice assistant."""

    def __init__(self, max_history: int = 10):
        self.conversation_history: List[Dict[str, str]] = []
        self.current_recipe: Optional[Dict[str, Any]] = None
        self.active_timers: List[Timer] = []
        self.max_history = max_history
        self.session_start = datetime.now()

    def add_message(self, role: str, content: str):
        """Add message to conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        # Keep only last max_history messages
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history * 2:]

    def set_recipe(self, recipe: Dict[str, Any]):
        """Set the current recipe context."""
        self.current_recipe = recipe
        logger.info(f"Set current recipe: {recipe.get('name', 'Unknown')}")

    def add_timer(self, duration_seconds: int, label: str = "Timer") -> Timer:
        """Add a new timer."""
        timer = Timer(duration_seconds, label)
        self.active_timers.append(timer)
        logger.info(f"Added timer: {label} for {duration_seconds}s")
        return timer

    def get_active_timers(self) -> List[Timer]:
        """Get all active timers."""
        # Remove finished timers
        self.active_timers = [t for t in self.active_timers if t.is_active]
        return self.active_timers

    def get_finished_timers(self) -> List[Timer]:
        """Get timers that just finished."""
        finished = [t for t in self.active_timers if t.is_finished() and t.is_active]
        for timer in finished:
            timer.cancel()
        return finished

    def cancel_all_timers(self):
        """Cancel all active timers."""
        for timer in self.active_timers:
            timer.cancel()
        self.active_timers = []

    def get_context_summary(self) -> str:
        """Get a summary of current context for AI."""
        context_parts = []

        # Add recipe context
        if self.current_recipe:
            recipe_name = self.current_recipe.get('name', 'Unknown Recipe')
            context_parts.append(f"Current recipe: {recipe_name}")

            if 'ingredients' in self.current_recipe:
                context_parts.append(
                    f"Ingredients: {', '.join(self.current_recipe['ingredients'][:5])}"
                )

            if 'current_step' in self.current_recipe:
                context_parts.append(
                    f"Current step: {self.current_recipe['current_step']}"
                )

        # Add active timers
        active_timers = self.get_active_timers()
        if active_timers:
            timer_info = [
                f"{t.label} ({t.time_remaining()}s remaining)"
                for t in active_timers
            ]
            context_parts.append(f"Active timers: {', '.join(timer_info)}")

        return "\n".join(context_parts) if context_parts else "No active context"


class VoiceAssistantService:
    """
    Service for real-time voice cooking assistance.

    Provides intelligent cooking guidance with voice interaction,
    timer management, unit conversion, and substitution suggestions.
    """

    # System prompt for cooking assistant
    COOKING_ASSISTANT_SYSTEM_PROMPT = """You are a friendly, helpful cooking assistant with expertise in culinary techniques, recipe guidance, and kitchen operations.

**Your Capabilities:**
1. **Recipe Guidance**: Provide clear, step-by-step cooking instructions
2. **Timers**: Help users set and manage cooking timers
3. **Unit Conversion**: Convert between metric and imperial measurements
4. **Substitutions**: Suggest ingredient substitutions when needed
5. **Troubleshooting**: Help solve cooking problems and answer questions

**Your Personality:**
- Warm and encouraging
- Patient and clear in explanations
- Practical and focused on results
- Safety-conscious about food handling and cooking

**Response Guidelines:**
- Keep responses concise and natural (suitable for voice)
- Use simple language, avoid jargon unless explaining
- Provide specific measurements and times
- Always prioritize food safety
- Be encouraging and positive

**Special Commands You Understand:**
- "Set a timer for X minutes" → Acknowledge and confirm timer
- "How many cups in X ml?" → Provide conversion
- "What can I substitute for X?" → Suggest alternatives
- "What's next?" → Provide next recipe step
- "Repeat that" → Repeat last instruction

**Current Context:**
{context_summary}

**Conversation History:**
{conversation_history}

Respond naturally and helpfully to the user's question."""

    # Unit conversion data
    UNIT_CONVERSIONS = {
        # Volume conversions (to ml)
        "cup": 236.588,
        "cups": 236.588,
        "tablespoon": 14.787,
        "tablespoons": 14.787,
        "tbsp": 14.787,
        "teaspoon": 4.929,
        "teaspoons": 4.929,
        "tsp": 4.929,
        "fluid_ounce": 29.574,
        "fluid_ounces": 29.574,
        "fl_oz": 29.574,
        "pint": 473.176,
        "pints": 473.176,
        "quart": 946.353,
        "quarts": 946.353,
        "gallon": 3785.41,
        "gallons": 3785.41,
        "liter": 1000,
        "liters": 1000,
        "ml": 1,
        "milliliter": 1,
        "milliliters": 1,

        # Weight conversions (to grams)
        "ounce": 28.3495,
        "ounces": 28.3495,
        "oz": 28.3495,
        "pound": 453.592,
        "pounds": 453.592,
        "lb": 453.592,
        "lbs": 453.592,
        "gram": 1,
        "grams": 1,
        "g": 1,
        "kilogram": 1000,
        "kilograms": 1000,
        "kg": 1000,
    }

    # Common ingredient substitutions
    SUBSTITUTIONS = {
        "butter": [
            "coconut oil (same amount)",
            "olive oil (3/4 amount for baking)",
            "applesauce (for baking, 1:1 ratio)"
        ],
        "milk": [
            "almond milk (1:1 ratio)",
            "oat milk (1:1 ratio)",
            "coconut milk (1:1 ratio)"
        ],
        "egg": [
            "flax egg (1 tbsp ground flax + 3 tbsp water)",
            "chia egg (1 tbsp chia seeds + 3 tbsp water)",
            "1/4 cup applesauce (for baking)"
        ],
        "sour_cream": [
            "Greek yogurt (1:1 ratio)",
            "plain yogurt (1:1 ratio)"
        ],
        "heavy_cream": [
            "coconut cream (1:1 ratio)",
            "milk + butter (3/4 cup milk + 1/4 cup melted butter)"
        ],
        "flour": [
            "almond flour (not 1:1, use 1.25 cups almond for 1 cup regular)",
            "oat flour (1:1 ratio for most recipes)"
        ],
        "sugar": [
            "honey (use 3/4 cup honey for 1 cup sugar, reduce liquid)",
            "maple syrup (use 3/4 cup syrup for 1 cup sugar, reduce liquid)"
        ],
    }

    def __init__(self, openai_service: Optional[OpenAIService] = None):
        """
        Initialize voice assistant service.

        Args:
            openai_service: OpenAI service instance
        """
        self.openai_service = openai_service or get_openai_service()
        # Store active sessions by user_id
        self.active_sessions: Dict[int, ConversationContext] = {}

    def get_or_create_session(self, user_id: int) -> ConversationContext:
        """Get or create a conversation session for user."""
        if user_id not in self.active_sessions:
            self.active_sessions[user_id] = ConversationContext()
        return self.active_sessions[user_id]

    async def transcribe_audio(self, audio_data: bytes, user_id: int) -> str:
        """
        Transcribe audio using OpenAI Whisper.

        Args:
            audio_data: Audio data in bytes (WAV, MP3, etc.)
            user_id: User ID for logging

        Returns:
            Transcribed text

        Raises:
            OpenAIServiceError: If transcription fails
        """
        try:
            logger.info(f"Transcribing audio for user {user_id}, size: {len(audio_data)} bytes")

            # Use OpenAI Whisper for transcription
            transcription = await self.openai_service.transcribe_audio(
                audio_data=audio_data,
                audio_format="wav"  # Default format, can be adjusted
            )

            logger.info(f"Transcribed: {transcription[:100]}...")
            return transcription

        except Exception as e:
            logger.error(f"Audio transcription failed: {e}", exc_info=True)
            raise OpenAIServiceError(f"Transcription failed: {str(e)}")

    def parse_timer_command(self, text: str) -> Optional[Tuple[int, str]]:
        """
        Parse timer command from text.

        Args:
            text: User's text input

        Returns:
            Tuple of (duration_seconds, label) or None if no timer command found
        """
        # Patterns for timer commands
        patterns = [
            r"set (?:a )?timer for (\d+) (minute|minutes|min|mins|second|seconds|sec|secs)",
            r"timer (?:for )?(\d+) (minute|minutes|min|mins|second|seconds|sec|secs)",
            r"(\d+) (minute|minutes|min|mins) timer",
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                amount = int(match.group(1))
                unit = match.group(2)

                # Convert to seconds
                if unit.startswith("min"):
                    duration = amount * 60
                else:  # seconds
                    duration = amount

                # Extract label if provided
                label_match = re.search(r"for (.+?) timer", text.lower())
                label = label_match.group(1) if label_match else f"{amount} {unit} timer"

                return (duration, label)

        return None

    def parse_conversion_query(self, text: str) -> Optional[str]:
        """
        Parse unit conversion query.

        Args:
            text: User's text input

        Returns:
            Conversion result or None if not a conversion query
        """
        # Pattern: "how many X in Y Z" or "convert Y Z to X"
        patterns = [
            r"how many (\w+) (?:in|are in) (\d+\.?\d*) (\w+)",
            r"convert (\d+\.?\d*) (\w+) to (\w+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                if "how many" in text.lower():
                    target_unit = match.group(1)
                    amount = float(match.group(2))
                    source_unit = match.group(3)
                else:  # convert pattern
                    amount = float(match.group(1))
                    source_unit = match.group(2)
                    target_unit = match.group(3)

                result = self.convert_units(amount, source_unit, target_unit)
                if result:
                    return result

        return None

    def convert_units(
        self, amount: float, from_unit: str, to_unit: str
    ) -> Optional[str]:
        """
        Convert between cooking units.

        Args:
            amount: Amount to convert
            from_unit: Source unit
            to_unit: Target unit

        Returns:
            Conversion result string or None if units not recognized
        """
        from_unit = from_unit.lower().replace(" ", "_")
        to_unit = to_unit.lower().replace(" ", "_")

        # Check if units are in our conversion table
        if from_unit not in self.UNIT_CONVERSIONS or to_unit not in self.UNIT_CONVERSIONS:
            return None

        # Get base values (ml for volume, grams for weight)
        from_base = self.UNIT_CONVERSIONS[from_unit]
        to_base = self.UNIT_CONVERSIONS[to_unit]

        # Check if both are volume or both are weight
        volume_units = {"cup", "cups", "tablespoon", "tablespoons", "tbsp", "teaspoon",
                       "teaspoons", "tsp", "fluid_ounce", "fluid_ounces", "fl_oz",
                       "pint", "pints", "quart", "quarts", "gallon", "gallons",
                       "liter", "liters", "ml", "milliliter", "milliliters"}

        from_is_volume = from_unit in volume_units
        to_is_volume = to_unit in volume_units

        if from_is_volume != to_is_volume:
            return None  # Can't convert between volume and weight

        # Convert
        base_amount = amount * from_base
        result = base_amount / to_base

        # Format result
        if result >= 1:
            formatted_result = f"{result:.2f}".rstrip('0').rstrip('.')
        else:
            formatted_result = f"{result:.3f}".rstrip('0').rstrip('.')

        return f"{amount} {from_unit} is approximately {formatted_result} {to_unit}"

    def get_substitution_suggestions(self, ingredient: str) -> Optional[List[str]]:
        """
        Get substitution suggestions for an ingredient.

        Args:
            ingredient: Ingredient to substitute

        Returns:
            List of substitution suggestions or None if not found
        """
        ingredient_lower = ingredient.lower().replace(" ", "_")

        # Check exact match
        if ingredient_lower in self.SUBSTITUTIONS:
            return self.SUBSTITUTIONS[ingredient_lower]

        # Check partial match
        for key, substitutions in self.SUBSTITUTIONS.items():
            if key in ingredient_lower or ingredient_lower in key:
                return substitutions

        return None

    async def generate_response(
        self, user_message: str, user_id: int, context: ConversationContext
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate intelligent response to user's message.

        Args:
            user_message: User's transcribed message
            user_id: User ID
            context: Conversation context

        Returns:
            Tuple of (response_text, metadata)
        """
        metadata: Dict[str, Any] = {
            "timer_set": False,
            "conversion_provided": False,
            "substitution_provided": False,
        }

        # Check for timer command
        timer_info = self.parse_timer_command(user_message)
        if timer_info:
            duration, label = timer_info
            timer = context.add_timer(duration, label)
            metadata["timer_set"] = True
            metadata["timer"] = timer.to_dict()

            minutes = duration // 60
            seconds = duration % 60
            time_str = f"{minutes} minute{'s' if minutes != 1 else ''}"
            if seconds > 0:
                time_str += f" and {seconds} second{'s' if seconds != 1 else ''}"

            response = f"Timer set for {time_str}. I'll let you know when it's done!"
            return response, metadata

        # Check for conversion query
        conversion = self.parse_conversion_query(user_message)
        if conversion:
            metadata["conversion_provided"] = True
            return conversion, metadata

        # Check for substitution query
        if "substitute" in user_message.lower() or "instead of" in user_message.lower():
            # Extract ingredient
            words = user_message.lower().replace("?", "").split()
            for i, word in enumerate(words):
                if word in ["substitute", "instead"]:
                    if i + 1 < len(words):
                        potential_ingredient = words[i + 1]
                        subs = self.get_substitution_suggestions(potential_ingredient)
                        if subs:
                            metadata["substitution_provided"] = True
                            response = f"Here are some substitutions for {potential_ingredient}:\n"
                            response += "\n".join(f"- {sub}" for sub in subs)
                            return response, metadata

        # Generate AI response using GPT-4
        try:
            # Build conversation history for AI
            messages = []

            # Add system prompt with context
            context_summary = context.get_context_summary()
            conversation_history = "\n".join(
                f"{msg['role']}: {msg['content']}"
                for msg in context.conversation_history[-6:]
            )

            system_prompt = self.COOKING_ASSISTANT_SYSTEM_PROMPT.format(
                context_summary=context_summary,
                conversation_history=conversation_history or "No previous conversation"
            )

            messages.append({"role": "system", "content": system_prompt})

            # Add recent conversation history
            for msg in context.conversation_history[-4:]:
                messages.append({"role": msg["role"], "content": msg["content"]})

            # Add current message
            messages.append({"role": "user", "content": user_message})

            # Generate response
            response = await self.openai_service.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=300,
            )

            return response, metadata

        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}", exc_info=True)
            return "I'm sorry, I'm having trouble processing that right now. Could you rephrase?", metadata

    async def text_to_speech(self, text: str, user_id: int) -> bytes:
        """
        Convert text to speech using OpenAI TTS.

        Args:
            text: Text to convert
            user_id: User ID for logging

        Returns:
            Audio data in bytes (MP3 format)

        Raises:
            OpenAIServiceError: If TTS fails
        """
        try:
            logger.info(f"Generating speech for user {user_id}: {text[:50]}...")

            # Use OpenAI TTS
            audio_data = await self.openai_service.text_to_speech(
                text=text,
                voice="nova",  # Friendly female voice for cooking
                model="tts-1",  # Standard quality (faster)
            )

            logger.info(f"Generated {len(audio_data)} bytes of audio")
            return audio_data

        except Exception as e:
            logger.error(f"Text-to-speech failed: {e}", exc_info=True)
            raise OpenAIServiceError(f"TTS failed: {str(e)}")

    async def process_voice_input(
        self, audio_data: bytes, user_id: int
    ) -> Tuple[str, str, bytes, Dict[str, Any]]:
        """
        Process complete voice interaction: transcribe -> respond -> synthesize.

        Args:
            audio_data: Input audio data
            user_id: User ID

        Returns:
            Tuple of (transcription, response_text, response_audio, metadata)
        """
        # Get user's context
        context = self.get_or_create_session(user_id)

        # 1. Transcribe audio
        transcription = await self.transcribe_audio(audio_data, user_id)

        # Add to conversation history
        context.add_message("user", transcription)

        # 2. Generate response
        response_text, metadata = await self.generate_response(
            transcription, user_id, context
        )

        # Add to conversation history
        context.add_message("assistant", response_text)

        # 3. Convert to speech
        response_audio = await self.text_to_speech(response_text, user_id)

        return transcription, response_text, response_audio, metadata

    def clear_session(self, user_id: int):
        """Clear conversation session for user."""
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]
            logger.info(f"Cleared session for user {user_id}")


# Singleton instance
_voice_assistant_service: Optional[VoiceAssistantService] = None


def get_voice_assistant_service() -> VoiceAssistantService:
    """Get voice assistant service singleton instance."""
    global _voice_assistant_service
    if _voice_assistant_service is None:
        _voice_assistant_service = VoiceAssistantService()
    return _voice_assistant_service
