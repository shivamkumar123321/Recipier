"""
Rate limiting middleware using SlowAPI.

Protects sensitive endpoints from abuse:
- Login attempts
- Password reset requests
- Registration
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000/hour"],  # Global rate limit
    storage_uri=settings.REDIS_URL,  # Use Redis for distributed rate limiting
)


# Custom limit decorators for different endpoint types
def auth_rate_limit():
    """Rate limit for authentication endpoints (stricter)."""
    return limiter.limit("5/minute")


def password_reset_rate_limit():
    """Rate limit for password reset requests (very strict)."""
    return limiter.limit("3/hour")


def registration_rate_limit():
    """Rate limit for user registration."""
    return limiter.limit("3/hour")


def api_rate_limit():
    """General API rate limit."""
    return limiter.limit("100/minute")
