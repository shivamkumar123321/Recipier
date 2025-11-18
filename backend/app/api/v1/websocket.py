"""
WebSocket endpoints for real-time updates.

Provides WebSocket connections for:
- Meal plan generation progress streaming
- Real-time notification push
"""

import asyncio
import json
from typing import Dict, Optional, Set

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import settings
from app.core.logging import get_logger
from app.services.intelligent_meal_plan_service import (
    get_intelligent_meal_plan_service,
)

logger = get_logger(__name__)

router = APIRouter()

# Connection managers for different WebSocket types
class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        # Active connections mapped by user_id
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """
        Accept and register a WebSocket connection.

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected for user {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        """
        Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            # Clean up empty sets
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_personal_message(self, message: dict, user_id: int):
        """
        Send a message to all connections for a specific user.

        Args:
            message: Message to send (will be JSON encoded)
            user_id: User ID
        """
        if user_id not in self.active_connections:
            logger.debug(f"No active connections for user {user_id}")
            return

        # Send to all connections for this user
        disconnected = []
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                disconnected.append(websocket)

        # Clean up disconnected sockets
        for websocket in disconnected:
            self.disconnect(websocket, user_id)

    async def broadcast(self, message: dict):
        """
        Broadcast a message to all connected clients.

        Args:
            message: Message to send (will be JSON encoded)
        """
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)


# Connection managers
notification_manager = ConnectionManager()
meal_plan_manager = ConnectionManager()


def verify_websocket_token(token: str) -> int:
    """
    Verify JWT token from WebSocket connection.

    Args:
        token: JWT token

    Returns:
        User ID from token

    Raises:
        JWTError: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: int = payload.get("sub")

        if user_id is None:
            raise JWTError("Invalid token payload")

        return user_id

    except JWTError as e:
        logger.error(f"WebSocket token verification failed: {e}")
        raise


@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for real-time notifications.

    Clients can connect to receive push notifications in real-time.

    Usage:
        ws://localhost:8000/api/v1/ws/notifications?token=<JWT_TOKEN>

    Message format (server -> client):
        {
            "type": "notification",
            "data": {
                "id": 123,
                "notification_type": "expiring_items",
                "title": "Item Expiring Soon!",
                "message": "Milk will expire tomorrow",
                "priority": "high",
                "created_at": "2025-11-18T12:00:00"
            }
        }
    """
    try:
        # Verify token and get user ID
        user_id = verify_websocket_token(token)

        # Connect WebSocket
        await notification_manager.connect(websocket, user_id)

        # Send welcome message
        await websocket.send_json(
            {
                "type": "connected",
                "message": "Connected to notification stream",
            }
        )

        try:
            # Keep connection alive and handle incoming messages
            while True:
                # Wait for messages from client (ping/pong, etc.)
                data = await websocket.receive_text()

                # Handle client messages
                try:
                    message = json.loads(data)

                    if message.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})

                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from user {user_id}: {data}")

        except WebSocketDisconnect:
            notification_manager.disconnect(websocket, user_id)
            logger.info(f"WebSocket disconnected for user {user_id}")

    except JWTError:
        await websocket.close(code=1008, reason="Invalid token")
        logger.warning("WebSocket connection rejected: Invalid token")

    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        await websocket.close(code=1011, reason="Internal server error")


@router.websocket("/ws/meal-plan-generation")
async def websocket_meal_plan_generation(
    websocket: WebSocket,
    token: str,
    days: int = 3,
    dietary_restrictions: Optional[str] = None,
    target_calories: Optional[int] = None,
):
    """
    WebSocket endpoint for streaming meal plan generation progress.

    Clients can connect to receive real-time updates during AI meal plan generation.

    Usage:
        ws://localhost:8000/api/v1/ws/meal-plan-generation?token=<JWT_TOKEN>&days=3&dietary_restrictions=vegetarian,gluten-free&target_calories=2000

    Query Parameters:
        - token: JWT authentication token (required)
        - days: Number of days for meal plan (3 or 7, default: 3)
        - dietary_restrictions: Comma-separated dietary restrictions (optional)
        - target_calories: Daily calorie target (optional)

    Message format (server -> client):
        {
            "type": "progress",
            "stage": "analyzing_inventory",
            "progress": 25,
            "message": "Analyzing your inventory and expiring items..."
        }

        {
            "type": "complete",
            "progress": 100,
            "message": "Meal plan generated successfully!",
            "meal_plan": {...}
        }

        {
            "type": "error",
            "stage": "generation_error",
            "message": "Error message"
        }
    """
    # Import here to avoid circular dependency
    from app.db.session import AsyncSessionLocal

    db: Optional[AsyncSession] = None

    try:
        # Verify token and get user ID
        user_id = verify_websocket_token(token)

        # Connect WebSocket
        await meal_plan_manager.connect(websocket, user_id)

        # Send welcome message
        await websocket.send_json(
            {
                "type": "connected",
                "message": "Connected to meal plan generation stream",
            }
        )

        # Parse dietary restrictions
        restrictions_list = (
            [r.strip() for r in dietary_restrictions.split(",")]
            if dietary_restrictions
            else None
        )

        # Create database session
        db = AsyncSessionLocal()

        try:
            # Get intelligent meal plan service
            intelligent_service = get_intelligent_meal_plan_service()

            # Generate meal plan with streaming updates
            meal_plan = await intelligent_service.generate_meal_plan_stream(
                db=db,
                user_id=user_id,
                websocket=websocket,
                days=days,
                dietary_restrictions=restrictions_list,
                target_calories=target_calories,
                prioritize_expiring=True,
                max_retries=3,
            )

            logger.info(
                f"Meal plan generated successfully via WebSocket for user {user_id}"
            )

        finally:
            # Close database session
            if db:
                await db.close()

        try:
            # Keep connection alive for additional messages
            while True:
                data = await websocket.receive_text()

                try:
                    message = json.loads(data)

                    if message.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                    elif message.get("type") == "generate":
                        # Client requested new generation
                        await websocket.send_json({
                            "type": "error",
                            "message": "New generation request not supported. Please reconnect."
                        })

                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from user {user_id}: {data}")

        except WebSocketDisconnect:
            meal_plan_manager.disconnect(websocket, user_id)
            logger.info(f"Meal plan WebSocket disconnected for user {user_id}")

    except JWTError:
        await websocket.close(code=1008, reason="Invalid token")
        logger.warning("WebSocket connection rejected: Invalid token")

    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "stage": "fatal_error",
                "message": f"Server error: {str(e)}"
            })
        except:
            pass
        await websocket.close(code=1011, reason="Internal server error")


@router.websocket("/ws/cooking-assistant")
async def websocket_cooking_assistant(
    websocket: WebSocket,
    token: str,
    recipe_id: Optional[int] = None,
):
    """
    WebSocket endpoint for real-time voice cooking assistant.

    Provides intelligent cooking guidance with voice interaction,
    timer management, unit conversion, and substitution suggestions.

    Usage:
        ws://localhost:8000/api/v1/ws/cooking-assistant?token=<JWT_TOKEN>&recipe_id=123

    Query Parameters:
        - token: JWT authentication token (required)
        - recipe_id: Optional recipe ID to load into context

    Message format (client -> server):
        {
            "type": "audio",
            "data": "<base64_encoded_audio>"
        }

        {
            "type": "text",
            "message": "How many cups in 500ml?"
        }

        {
            "type": "set_recipe",
            "recipe": {
                "name": "Chocolate Chip Cookies",
                "ingredients": [...],
                "instructions": [...]
            }
        }

        {
            "type": "ping"
        }

    Message format (server -> client):
        {
            "type": "transcription",
            "text": "Set a timer for 10 minutes"
        }

        {
            "type": "response",
            "text": "Timer set for 10 minutes!",
            "audio": "<base64_encoded_audio>",
            "metadata": {
                "timer_set": true,
                "timer": {...}
            }
        }

        {
            "type": "timer_finished",
            "timer": {
                "label": "10 minute timer",
                "duration_seconds": 600
            }
        }

        {
            "type": "error",
            "message": "Error message"
        }
    """
    # Import here to avoid circular dependency
    import base64
    from app.db.session import AsyncSessionLocal
    from app.services.voice_assistant_service import get_voice_assistant_service

    db: Optional[AsyncSession] = None

    try:
        # Verify token and get user ID
        user_id = verify_websocket_token(token)

        # Connect WebSocket
        await websocket.accept()

        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to cooking assistant",
        })

        logger.info(f"Cooking assistant WebSocket connected for user {user_id}")

        # Get voice assistant service
        voice_service = get_voice_assistant_service()
        context = voice_service.get_or_create_session(user_id)

        # Load recipe if recipe_id provided
        if recipe_id:
            db = AsyncSessionLocal()
            try:
                from app.services.recipe_service import recipe_service
                recipe = await recipe_service.get_recipe_by_id(db, recipe_id)
                if recipe:
                    context.set_recipe({
                        "name": recipe.name,
                        "ingredients": [ing.name for ing in recipe.ingredients] if recipe.ingredients else [],
                        "instructions": [inst.instruction for inst in recipe.instructions] if recipe.instructions else [],
                    })
                    await websocket.send_json({
                        "type": "recipe_loaded",
                        "recipe_name": recipe.name,
                    })
            finally:
                if db:
                    await db.close()

        # Timer check task
        async def check_timers():
            """Background task to check for finished timers."""
            while True:
                try:
                    finished_timers = context.get_finished_timers()
                    for timer in finished_timers:
                        await websocket.send_json({
                            "type": "timer_finished",
                            "timer": timer.to_dict(),
                        })
                        logger.info(f"Timer finished for user {user_id}: {timer.label}")

                    await asyncio.sleep(1)  # Check every second
                except Exception as e:
                    logger.error(f"Timer check error: {e}")
                    break

        # Start timer check task
        timer_task = asyncio.create_task(check_timers())

        try:
            # Handle incoming messages
            while True:
                data = await websocket.receive_text()

                try:
                    message = json.loads(data)
                    msg_type = message.get("type")

                    if msg_type == "audio":
                        # Process voice input
                        try:
                            # Decode base64 audio
                            audio_b64 = message.get("data", "")
                            audio_bytes = base64.b64decode(audio_b64)

                            # Process voice input (transcribe -> respond -> TTS)
                            transcription, response_text, response_audio, metadata = (
                                await voice_service.process_voice_input(audio_bytes, user_id)
                            )

                            # Send transcription
                            await websocket.send_json({
                                "type": "transcription",
                                "text": transcription,
                            })

                            # Send response with audio
                            await websocket.send_json({
                                "type": "response",
                                "text": response_text,
                                "audio": base64.b64encode(response_audio).decode('utf-8'),
                                "metadata": metadata,
                            })

                            logger.info(f"Processed voice input for user {user_id}")

                        except Exception as e:
                            logger.error(f"Voice processing error: {e}", exc_info=True)
                            await websocket.send_json({
                                "type": "error",
                                "message": "Failed to process voice input",
                            })

                    elif msg_type == "text":
                        # Process text input (no audio transcription)
                        try:
                            user_text = message.get("message", "")

                            # Add to conversation
                            context.add_message("user", user_text)

                            # Generate response
                            response_text, metadata = await voice_service.generate_response(
                                user_text, user_id, context
                            )

                            # Add to conversation
                            context.add_message("assistant", response_text)

                            # Generate TTS
                            response_audio = await voice_service.text_to_speech(response_text, user_id)

                            # Send response
                            await websocket.send_json({
                                "type": "response",
                                "text": response_text,
                                "audio": base64.b64encode(response_audio).decode('utf-8'),
                                "metadata": metadata,
                            })

                        except Exception as e:
                            logger.error(f"Text processing error: {e}", exc_info=True)
                            await websocket.send_json({
                                "type": "error",
                                "message": "Failed to process text input",
                            })

                    elif msg_type == "set_recipe":
                        # Set recipe context
                        recipe_data = message.get("recipe", {})
                        context.set_recipe(recipe_data)
                        await websocket.send_json({
                            "type": "recipe_set",
                            "recipe_name": recipe_data.get("name", "Unknown"),
                        })

                    elif msg_type == "get_timers":
                        # Get active timers
                        active_timers = context.get_active_timers()
                        await websocket.send_json({
                            "type": "active_timers",
                            "timers": [t.to_dict() for t in active_timers],
                        })

                    elif msg_type == "cancel_timers":
                        # Cancel all timers
                        context.cancel_all_timers()
                        await websocket.send_json({
                            "type": "timers_cancelled",
                        })

                    elif msg_type == "ping":
                        await websocket.send_json({"type": "pong"})

                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Unknown message type: {msg_type}",
                        })

                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from user {user_id}: {data}")
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid JSON format",
                    })

        except WebSocketDisconnect:
            logger.info(f"Cooking assistant WebSocket disconnected for user {user_id}")
        finally:
            # Cancel timer task
            timer_task.cancel()
            try:
                await timer_task
            except asyncio.CancelledError:
                pass

    except JWTError:
        await websocket.close(code=1008, reason="Invalid token")
        logger.warning("WebSocket connection rejected: Invalid token")

    except Exception as e:
        logger.error(f"Cooking assistant WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Server error: {str(e)}",
            })
        except:
            pass
        await websocket.close(code=1011, reason="Internal server error")


async def simulate_meal_plan_generation(websocket: WebSocket):
    """
    Simulate AI meal plan generation progress.

    PLACEHOLDER: In production, this would receive real-time updates
    from the OpenAI API during meal plan generation.

    Args:
        websocket: WebSocket connection
    """
    stages = [
        {"stage": "analyzing_preferences", "progress": 10, "message": "Analyzing dietary preferences..."},
        {"stage": "fetching_recipes", "progress": 30, "message": "Fetching matching recipes..."},
        {"stage": "balancing_nutrition", "progress": 50, "message": "Balancing nutritional targets..."},
        {"stage": "scheduling_meals", "progress": 70, "message": "Scheduling meals across the week..."},
        {"stage": "finalizing", "progress": 90, "message": "Finalizing meal plan..."},
    ]

    for stage in stages:
        await websocket.send_json({
            "type": "progress",
            **stage,
        })
        await asyncio.sleep(1)  # Simulate processing time

    # Send completion message
    await websocket.send_json({
        "type": "complete",
        "meal_plan_id": 123,  # Would be real ID in production
        "message": "Meal plan generated successfully!",
    })


async def send_notification_to_user(user_id: int, notification: dict):
    """
    Send a notification to a specific user via WebSocket.

    This function can be called from services to push notifications in real-time.

    Args:
        user_id: User ID
        notification: Notification data to send
    """
    await notification_manager.send_personal_message(
        {
            "type": "notification",
            "data": notification,
        },
        user_id,
    )


async def broadcast_notification(notification: dict):
    """
    Broadcast a notification to all connected users.

    Args:
        notification: Notification data to send
    """
    await notification_manager.broadcast(
        {
            "type": "notification",
            "data": notification,
        }
    )
