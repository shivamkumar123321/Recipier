"""
Authentication service for user registration, login, and verification.

Handles:
- User registration with email verification
- Login with JWT tokens
- Token refresh
- Email verification
- Password reset flow
- Token blacklisting (logout)
"""

from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import blacklist_token, is_token_blacklisted
from app.core.config import settings
from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    create_verification_token,
    get_password_hash,
    verify_password,
    verify_password_reset_token,
    verify_token,
    verify_verification_token,
)
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.services.email_service import email_service

logger = get_logger(__name__)


class AuthService:
    """Service for authentication operations."""

    async def register_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        full_name: Optional[str] = None,
    ) -> User:
        """
        Register a new user.

        Args:
            db: Database session
            email: User email address
            password: Plain text password
            full_name: Optional full name

        Returns:
            Created user object

        Raises:
            ConflictException: If email already exists
            ValidationException: If password is too weak
        """
        # Validate password strength
        self._validate_password(password)

        # Check if email already exists
        if await user_repository.email_exists(db, email):
            raise ConflictException(
                "Email already registered",
                error_code="EMAIL_ALREADY_EXISTS",
            )

        # Create user
        hashed_password = get_password_hash(password)
        user = await user_repository.create(
            db,
            {
                "email": email.lower(),
                "hashed_password": hashed_password,
                "full_name": full_name,
                "is_active": True,
                "is_verified": False,  # Requires email verification
            },
        )

        await db.commit()
        await db.refresh(user)

        # Send verification email
        await self._send_verification_email(user.email)

        logger.info(f"User registered: {user.email}")

        return user

    async def login_user(
        self, db: AsyncSession, email: str, password: str
    ) -> Tuple[str, str, User]:
        """
        Authenticate user and generate tokens.

        Args:
            db: Database session
            email: User email address
            password: Plain text password

        Returns:
            Tuple of (access_token, refresh_token, user)

        Raises:
            UnauthorizedException: If credentials are invalid
        """
        # Get user by email
        user = await user_repository.get_by_email(db, email)

        if not user or not verify_password(password, user.hashed_password):
            logger.warning(f"Failed login attempt for: {email}")
            raise UnauthorizedException(
                "Incorrect email or password",
                error_code="INVALID_CREDENTIALS",
            )

        if not user.is_active:
            raise UnauthorizedException(
                "Account is inactive",
                error_code="ACCOUNT_INACTIVE",
            )

        # Note: We allow login even if email is not verified
        # but could enforce verification here if needed:
        # if not user.is_verified:
        #     raise UnauthorizedException("Email not verified")

        # Create tokens
        token_data = {"sub": user.id}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        logger.info(f"User logged in: {user.email}")

        return access_token, refresh_token, user

    async def refresh_tokens(
        self, db: AsyncSession, refresh_token: str
    ) -> Tuple[str, str]:
        """
        Refresh access token using refresh token.

        Args:
            db: Database session
            refresh_token: Valid refresh token

        Returns:
            Tuple of (new_access_token, new_refresh_token)

        Raises:
            UnauthorizedException: If refresh token is invalid
        """
        # Check if token is blacklisted
        if await is_token_blacklisted(refresh_token):
            raise UnauthorizedException(
                "Token has been revoked",
                error_code="TOKEN_REVOKED",
            )

        # Verify refresh token
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException(
                "Invalid refresh token",
                error_code="INVALID_REFRESH_TOKEN",
            )

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException(
                "Invalid token payload",
                error_code="INVALID_TOKEN_PAYLOAD",
            )

        # Verify user still exists and is active
        user = await user_repository.get(db, user_id)

        if not user or not user.is_active:
            raise UnauthorizedException(
                "User not found or inactive",
                error_code="USER_NOT_FOUND",
            )

        # Create new tokens
        token_data = {"sub": user.id}
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        logger.info(f"Tokens refreshed for user: {user.email}")

        return new_access_token, new_refresh_token

    async def verify_email(
        self, db: AsyncSession, verification_token: str
    ) -> User:
        """
        Verify user email with verification token.

        Args:
            db: Database session
            verification_token: Email verification token

        Returns:
            Updated user object

        Raises:
            UnauthorizedException: If token is invalid
            NotFoundException: If user not found
        """
        # Verify token
        email = verify_verification_token(verification_token)

        if not email:
            raise UnauthorizedException(
                "Invalid or expired verification token",
                error_code="INVALID_VERIFICATION_TOKEN",
            )

        # Get user
        user = await user_repository.get_by_email(db, email)

        if not user:
            raise NotFoundException(
                "User not found",
                error_code="USER_NOT_FOUND",
            )

        # Update verification status
        if user.is_verified:
            logger.info(f"Email already verified: {email}")
            return user

        user.is_verified = True
        await db.commit()
        await db.refresh(user)

        logger.info(f"Email verified: {email}")

        return user

    async def resend_verification_email(
        self, db: AsyncSession, email: str
    ) -> bool:
        """
        Resend verification email.

        Args:
            db: Database session
            email: User email address

        Returns:
            True if email sent successfully

        Raises:
            NotFoundException: If user not found
            ValidationException: If email already verified
        """
        user = await user_repository.get_by_email(db, email)

        if not user:
            raise NotFoundException(
                "User not found",
                error_code="USER_NOT_FOUND",
            )

        if user.is_verified:
            raise ValidationException(
                "Email already verified",
                error_code="EMAIL_ALREADY_VERIFIED",
            )

        # Send verification email
        await self._send_verification_email(user.email)

        logger.info(f"Verification email resent: {email}")

        return True

    async def request_password_reset(
        self, db: AsyncSession, email: str
    ) -> bool:
        """
        Send password reset email.

        Args:
            db: Database session
            email: User email address

        Returns:
            Always True (don't reveal if email exists)
        """
        user = await user_repository.get_by_email(db, email)

        # Always return success to prevent email enumeration
        if not user:
            logger.info(f"Password reset requested for non-existent email: {email}")
            return True

        if not user.is_active:
            logger.info(f"Password reset requested for inactive account: {email}")
            return True

        # Send password reset email
        await self._send_password_reset_email(user.email)

        logger.info(f"Password reset email sent: {email}")

        return True

    async def reset_password(
        self, db: AsyncSession, reset_token: str, new_password: str
    ) -> User:
        """
        Reset user password with reset token.

        Args:
            db: Database session
            reset_token: Password reset token
            new_password: New plain text password

        Returns:
            Updated user object

        Raises:
            UnauthorizedException: If token is invalid
            NotFoundException: If user not found
            ValidationException: If password is too weak
        """
        # Validate password strength
        self._validate_password(new_password)

        # Verify token
        email = verify_password_reset_token(reset_token)

        if not email:
            raise UnauthorizedException(
                "Invalid or expired reset token",
                error_code="INVALID_RESET_TOKEN",
            )

        # Get user
        user = await user_repository.get_by_email(db, email)

        if not user:
            raise NotFoundException(
                "User not found",
                error_code="USER_NOT_FOUND",
            )

        # Update password
        user.hashed_password = get_password_hash(new_password)
        await db.commit()
        await db.refresh(user)

        # Send confirmation email
        await email_service.send_password_changed_notification(user.email)

        logger.info(f"Password reset successful: {email}")

        return user

    async def logout_user(
        self, access_token: str, refresh_token: Optional[str] = None
    ) -> bool:
        """
        Logout user by blacklisting tokens.

        Args:
            access_token: Access token to blacklist
            refresh_token: Optional refresh token to blacklist

        Returns:
            True if logout successful
        """
        # Get token expiration time
        payload = verify_token(access_token)
        if payload:
            exp = payload.get("exp")
            if exp:
                # Calculate remaining time until expiration
                expires_in = exp - int(datetime.utcnow().timestamp())
                if expires_in > 0:
                    await blacklist_token(access_token, expires_in)

        # Blacklist refresh token if provided
        if refresh_token:
            refresh_payload = verify_token(refresh_token)
            if refresh_payload:
                exp = refresh_payload.get("exp")
                if exp:
                    expires_in = exp - int(datetime.utcnow().timestamp())
                    if expires_in > 0:
                        await blacklist_token(refresh_token, expires_in)

        logger.info("User logged out successfully")

        return True

    async def _send_verification_email(self, email: str) -> bool:
        """
        Send verification email to user.

        Args:
            email: User email address

        Returns:
            True if sent successfully
        """
        token = create_verification_token(email)

        # Build verification URL
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
        verification_url = f"{frontend_url}/verify-email?token={token}"

        return await email_service.send_verification_email(email, verification_url)

    async def _send_password_reset_email(self, email: str) -> bool:
        """
        Send password reset email to user.

        Args:
            email: User email address

        Returns:
            True if sent successfully
        """
        token = create_password_reset_token(email)

        # Build reset URL
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
        reset_url = f"{frontend_url}/reset-password?token={token}"

        return await email_service.send_password_reset_email(email, reset_url)

    def _validate_password(self, password: str) -> None:
        """
        Validate password strength.

        Args:
            password: Plain text password

        Raises:
            ValidationException: If password doesn't meet requirements
        """
        if len(password) < 8:
            raise ValidationException(
                "Password must be at least 8 characters long",
                error_code="PASSWORD_TOO_SHORT",
            )

        # Could add more requirements:
        # - At least one uppercase letter
        # - At least one lowercase letter
        # - At least one digit
        # - At least one special character


# Singleton instance
auth_service = AuthService()
