"""
Security utilities for authentication and authorization.

Provides functions for:
- Password hashing and verification (bcrypt)
- JWT token generation and validation
- Token payload management
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate JWT access token.

    Args:
        data: Payload data to encode in token (should include 'sub' for user ID)
        expires_delta: Token expiration time (defaults to ACCESS_TOKEN_EXPIRE_MINUTES)

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow(),
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Generate JWT refresh token.

    Args:
        data: Payload data to encode in token (should include 'sub' for user ID)

    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow(),
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token string to verify

    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Bcrypt hashed password
    """
    return pwd_context.hash(password)


def create_verification_token(email: str) -> str:
    """
    Generate email verification token.

    Args:
        email: User email address

    Returns:
        Encoded JWT verification token (valid for 24 hours)
    """
    to_encode = {
        "sub": email,
        "type": "email_verification",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_password_reset_token(email: str) -> str:
    """
    Generate password reset token.

    Args:
        email: User email address

    Returns:
        Encoded JWT password reset token (valid for 1 hour)
    """
    to_encode = {
        "sub": email,
        "type": "password_reset",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_verification_token(token: str) -> Optional[str]:
    """
    Verify email verification token.

    Args:
        token: Email verification token

    Returns:
        Email address if valid, None otherwise
    """
    payload = verify_token(token)
    if not payload or payload.get("type") != "email_verification":
        return None
    return payload.get("sub")


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify password reset token.

    Args:
        token: Password reset token

    Returns:
        Email address if valid, None otherwise
    """
    payload = verify_token(token)
    if not payload or payload.get("type") != "password_reset":
        return None
    return payload.get("sub")
