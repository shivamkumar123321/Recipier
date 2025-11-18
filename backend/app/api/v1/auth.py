"""
Authentication endpoints.

Provides:
- User registration with email verification
- Login/logout with JWT tokens
- Token refresh
- Email verification
- Password reset flow
- Rate limiting on sensitive endpoints
"""

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import UnauthorizedException
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    EmailVerificationRequest,
    LogoutRequest,
    PasswordChangeRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    ResendVerificationRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth_service import auth_service

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account. A verification email will be sent.",
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Register a new user account.

    A verification email will be sent to the provided email address.
    The user can log in immediately but some features may require email verification.

    Args:
        user_data: User registration data (email, password)
        db: Database session

    Returns:
        Created user object (without password)

    Raises:
        ConflictException: If email already exists
        ValidationException: If password is too weak
    """
    user = await auth_service.register_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        full_name=getattr(user_data, "full_name", None),
    )

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="Authenticate and receive access/refresh tokens.",
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate user and return JWT tokens.

    Args:
        credentials: User login credentials (email, password)
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        UnauthorizedException: If credentials are invalid or account is inactive
    """
    access_token, refresh_token, user = await auth_service.login_user(
        db=db,
        email=credentials.email,
        password=credentials.password,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get new access token using refresh token.",
)
async def refresh_token(
    request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Refresh access token using refresh token.

    Args:
        request: Token refresh request with refresh token
        db: Database session

    Returns:
        New access and refresh tokens

    Raises:
        UnauthorizedException: If refresh token is invalid or revoked
    """
    access_token, refresh_token = await auth_service.refresh_tokens(
        db=db,
        refresh_token=request.refresh_token,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get current authenticated user information.",
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current authenticated user information.

    Requires valid JWT token in Authorization header.

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
    description="Logout user by blacklisting tokens.",
)
async def logout(
    request: LogoutRequest,
    current_user: User = Depends(get_current_user),
    authorization: str = Header(None),
) -> None:
    """
    Logout current user by blacklisting tokens.

    Blacklists both access and refresh tokens to prevent reuse.

    Args:
        request: Optional logout request with refresh token
        current_user: Current authenticated user
        authorization: Authorization header with access token
    """
    # Extract access token from Authorization header
    access_token = None
    if authorization and authorization.startswith("Bearer "):
        access_token = authorization.replace("Bearer ", "")

    if access_token:
        await auth_service.logout_user(
            access_token=access_token,
            refresh_token=request.refresh_token,
        )


@router.post(
    "/verify-email",
    response_model=UserResponse,
    summary="Verify email",
    description="Verify user email with verification token.",
)
async def verify_email(
    request: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Verify user email with verification token.

    Args:
        request: Email verification request with token
        db: Database session

    Returns:
        Updated user object

    Raises:
        UnauthorizedException: If token is invalid or expired
        NotFoundException: If user not found
    """
    user = await auth_service.verify_email(
        db=db,
        verification_token=request.token,
    )

    return user


@router.post(
    "/resend-verification",
    status_code=status.HTTP_200_OK,
    summary="Resend verification email",
    description="Resend email verification link.",
)
async def resend_verification_email(
    request: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Resend verification email to user.

    Args:
        request: Resend verification request with email
        db: Database session

    Returns:
        Success message

    Raises:
        NotFoundException: If user not found
        ValidationException: If email already verified
    """
    await auth_service.resend_verification_email(
        db=db,
        email=request.email,
    )

    return {"message": "Verification email sent successfully"}


@router.post(
    "/password-reset/request",
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Request password reset link via email.",
)
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Request password reset email.

    Always returns success to prevent email enumeration.

    Args:
        request: Password reset request with email
        db: Database session

    Returns:
        Success message
    """
    await auth_service.request_password_reset(
        db=db,
        email=request.email,
    )

    return {
        "message": "If the email exists, a password reset link has been sent"
    }


@router.post(
    "/password-reset/confirm",
    response_model=UserResponse,
    summary="Reset password",
    description="Reset password with reset token.",
)
async def reset_password(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Reset password with reset token.

    Args:
        request: Password reset confirmation with token and new password
        db: Database session

    Returns:
        Updated user object

    Raises:
        UnauthorizedException: If token is invalid or expired
        NotFoundException: If user not found
        ValidationException: If password is too weak
    """
    user = await auth_service.reset_password(
        db=db,
        reset_token=request.token,
        new_password=request.new_password,
    )

    return user


@router.post(
    "/password/change",
    response_model=UserResponse,
    summary="Change password",
    description="Change password for logged-in user.",
)
async def change_password(
    request: PasswordChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Change password for logged-in user.

    Requires current password for verification.

    Args:
        request: Password change request with current and new password
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated user object

    Raises:
        UnauthorizedException: If current password is incorrect
        ValidationException: If new password is too weak
    """
    # Verify current password through login
    await auth_service.login_user(
        db=db,
        email=current_user.email,
        password=request.current_password,
    )

    # Reset password (reuse password reset logic)
    from app.core.security import create_password_reset_token

    reset_token = create_password_reset_token(current_user.email)
    user = await auth_service.reset_password(
        db=db,
        reset_token=reset_token,
        new_password=request.new_password,
    )

    return user
