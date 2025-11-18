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
