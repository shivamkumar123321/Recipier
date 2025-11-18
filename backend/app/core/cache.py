"""
Redis cache utilities for token blacklisting and general caching.

Provides functions for:
- Token blacklisting (logout)
- General key-value caching
- TTL-based expiration
"""

import json
from datetime import timedelta
from typing import Any, Optional

import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Global Redis connection pool
_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """
    Get Redis client instance.

    Returns:
        Redis client with connection pooling
    """
    global _redis_client

    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=10,
        )
        logger.info("Redis connection pool created")

    return _redis_client


async def close_redis() -> None:
    """Close Redis connection pool."""
    global _redis_client

    if _redis_client:
        await _redis_client.close()
        logger.info("Redis connection pool closed")
        _redis_client = None


async def blacklist_token(token: str, expires_in: int) -> bool:
    """
    Blacklist a JWT token (for logout).

    Args:
        token: JWT token to blacklist
        expires_in: Token expiration time in seconds

    Returns:
        True if blacklisted successfully
    """
    try:
        redis_client = await get_redis()
        key = f"blacklist:token:{token}"

        # Store token with expiration matching token's exp time
        await redis_client.setex(key, expires_in, "blacklisted")

        logger.info(f"Token blacklisted: {token[:20]}...")
        return True
    except Exception as e:
        logger.error(f"Failed to blacklist token: {e}")
        return False


async def is_token_blacklisted(token: str) -> bool:
    """
    Check if a token is blacklisted.

    Args:
        token: JWT token to check

    Returns:
        True if token is blacklisted
    """
    try:
        redis_client = await get_redis()
        key = f"blacklist:token:{token}"

        result = await redis_client.exists(key)
        return result > 0
    except Exception as e:
        logger.error(f"Failed to check token blacklist: {e}")
        # Fail open - don't block users if Redis is down
        return False


async def cache_set(
    key: str,
    value: Any,
    expires_in: Optional[int] = None
) -> bool:
    """
    Set a value in cache.

    Args:
        key: Cache key
        value: Value to cache (will be JSON serialized)
        expires_in: Expiration time in seconds (None = no expiration)

    Returns:
        True if cached successfully
    """
    try:
        redis_client = await get_redis()

        # Serialize value to JSON
        serialized_value = json.dumps(value)

        if expires_in:
            await redis_client.setex(key, expires_in, serialized_value)
        else:
            await redis_client.set(key, serialized_value)

        logger.debug(f"Cached key: {key}")
        return True
    except Exception as e:
        logger.error(f"Failed to cache key {key}: {e}")
        return False


async def cache_get(key: str) -> Optional[Any]:
    """
    Get a value from cache.

    Args:
        key: Cache key

    Returns:
        Cached value if exists, None otherwise
    """
    try:
        redis_client = await get_redis()

        value = await redis_client.get(key)

        if value:
            # Deserialize from JSON
            return json.loads(value)

        return None
    except Exception as e:
        logger.error(f"Failed to get cached key {key}: {e}")
        return None


async def cache_delete(key: str) -> bool:
    """
    Delete a key from cache.

    Args:
        key: Cache key to delete

    Returns:
        True if deleted successfully
    """
    try:
        redis_client = await get_redis()

        await redis_client.delete(key)

        logger.debug(f"Deleted cache key: {key}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete cache key {key}: {e}")
        return False


async def cache_exists(key: str) -> bool:
    """
    Check if a key exists in cache.

    Args:
        key: Cache key to check

    Returns:
        True if key exists
    """
    try:
        redis_client = await get_redis()

        result = await redis_client.exists(key)
        return result > 0
    except Exception as e:
        logger.error(f"Failed to check cache key {key}: {e}")
        return False
