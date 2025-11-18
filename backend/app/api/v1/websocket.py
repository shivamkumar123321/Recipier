"""
WebSocket endpoints for real-time updates.

Provides WebSocket connections for:
- Meal plan generation progress streaming
- Real-time notification push
"""

import asyncio
import json
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt

from app.core.config import settings
from app.core.logging import get_logger

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
async def websocket_meal_plan_generation(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for streaming meal plan generation progress.

    Clients can connect to receive real-time updates during AI meal plan generation.

    Usage:
        ws://localhost:8000/api/v1/ws/meal-plan-generation?token=<JWT_TOKEN>

    Message format (server -> client):
        {
            "type": "progress",
            "stage": "analyzing_preferences",
            "progress": 25,
            "message": "Analyzing dietary preferences..."
        }

        {
            "type": "meal_added",
            "meal": {
                "date": "2025-11-18",
                "meal_type": "breakfast",
                "recipe_name": "Avocado Toast"
            }
        }

        {
            "type": "complete",
            "meal_plan_id": 123,
            "message": "Meal plan generated successfully!"
        }
    """
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

        # PLACEHOLDER: Simulate meal plan generation progress
        # In production, this would receive real-time updates from AI generation service
        await simulate_meal_plan_generation(websocket)

        try:
            # Keep connection alive
            while True:
                data = await websocket.receive_text()

                try:
                    message = json.loads(data)

                    if message.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})

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
