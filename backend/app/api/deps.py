"""
Common dependencies for API endpoints.

Provides reusable dependencies for:
- Database sessions
- Current user authentication
- Pagination parameters
- Service instances
"""

from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.security import verify_token
from app.db.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        token: JWT access token from Authorization header
        db: Database session

    Returns:
        Current user object

    Raises:
        UnauthorizedException: If token is invalid or user not found
    """
    # Verify token
    payload = verify_token(token)
    if payload is None:
        raise UnauthorizedException("Could not validate credentials")

    # Extract user ID from token
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Invalid token payload")

    # Get user from database
    user_repo = UserRepository()
    user = await user_repo.get(db, user_id)

    if user is None:
        raise UnauthorizedException("User not found")

    if not user.is_active:
        raise UnauthorizedException("User account is inactive")

    return user


async def get_current_active_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user who is active and email verified.

    Args:
        current_user: Current authenticated user

    Returns:
        Verified user object

    Raises:
        HTTPException: If user email is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email to access this resource.",
        )
    return current_user


class PaginationParams:
    """
    Common pagination parameters for list endpoints.

    Attributes:
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return
    """

    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(
            20,
            ge=1,
            le=100,
            description="Maximum number of records to return (max 100)",
        ),
    ):
        self.skip = skip
        self.limit = limit


# Repository dependencies
def get_user_repository() -> UserRepository:
    """Get user repository instance."""
    return UserRepository()


# Note: Add more repository dependencies as you create them
# def get_meal_repository() -> MealRepository:
#     return MealRepository()
