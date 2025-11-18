"""
Authentication endpoints.

Provides user registration, login, token refresh, and email verification.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.db.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Register a new user account.

    Args:
        user_data: User registration data (email, password)
        db: Database session

    Returns:
        Created user object

    Raises:
        ConflictException: If email already exists
    """
    user_repo = UserRepository()

    # Check if email already exists
    if await user_repo.email_exists(db, user_data.email):
        raise ConflictException("Email already registered")

    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = await user_repo.create(
        db,
        {
            "email": user_data.email.lower(),
            "hashed_password": hashed_password,
            "is_active": True,
            "is_verified": False,  # Email verification required
        },
    )

    await db.commit()

    # TODO: Send verification email
    # await send_verification_email(user.email)

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate user and return access/refresh tokens.

    Args:
        credentials: User login credentials (email, password)
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        UnauthorizedException: If credentials are invalid
    """
    user_repo = UserRepository()

    # Get user by email
    user = await user_repo.get_by_email(db, credentials.email)

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise UnauthorizedException("Incorrect email or password")

    if not user.is_active:
        raise UnauthorizedException("User account is inactive")

    # Create tokens
    token_data = {"sub": user.id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Refresh access token using refresh token.

    Args:
        refresh_token: Valid refresh token
        db: Database session

    Returns:
        New access and refresh tokens

    Raises:
        UnauthorizedException: If refresh token is invalid
    """
    # Verify refresh token
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise UnauthorizedException("Invalid refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")

    # Verify user still exists and is active
    user_repo = UserRepository()
    user = await user_repo.get(db, user_id)

    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive")

    # Create new tokens
    token_data = {"sub": user.id}
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current authenticated user information.

    Args:
        current_user: Current user from JWT token

    Returns:
        Current user object
    """
    return current_user


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user",
)
async def logout(
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Logout current user.

    Note: With JWT tokens, logout is handled client-side by removing the token.
    This endpoint is provided for consistency and can be extended to
    implement token blacklisting if needed.

    Args:
        current_user: Current authenticated user
    """
    # TODO: Implement token blacklisting in Redis if needed
    # await blacklist_token(token)
    pass
