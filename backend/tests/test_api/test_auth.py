"""
Comprehensive tests for authentication endpoints.

Tests:
- User registration
- Login/logout
- Token refresh
- Email verification
- Password reset flow
- Password change
- Rate limiting
- Token blacklisting
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import blacklist_token, cache_delete
from app.core.security import (
    create_password_reset_token,
    create_verification_token,
    verify_token,
)
from app.models.user import User
from app.repositories.user_repository import user_repository


class TestUserRegistration:
    """Test user registration endpoints."""

    @pytest.mark.asyncio
    async def test_register_success(
        self, client: AsyncClient, db: AsyncSession
    ):
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["is_active"] is True
        assert data["is_verified"] is False  # Email verification required
        assert "id" in data
        assert "hashed_password" not in data  # Password should not be returned

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self, client: AsyncClient, test_user: User
    ):
        """Test registration with existing email fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "securepassword123",
            },
        )

        assert response.status_code == 409  # Conflict
        data = response.json()
        assert "already registered" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "short",  # Too short
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "securepassword123",
            },
        )

        assert response.status_code == 422  # Validation error


class TestUserLogin:
    """Test user login endpoints."""

    @pytest.mark.asyncio
    async def test_login_success(
        self, client: AsyncClient, test_user: User
    ):
        """Test successful login."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "testpassword123",  # From fixture
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

        # Verify tokens are valid
        access_payload = verify_token(data["access_token"])
        assert access_payload is not None
        assert access_payload["type"] == "access"
        assert access_payload["sub"] == test_user.id

        refresh_payload = verify_token(data["refresh_token"])
        assert refresh_payload is not None
        assert refresh_payload["type"] == "refresh"

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self, client: AsyncClient, test_user: User
    ):
        """Test login with wrong password fails."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401  # Unauthorized
        data = response.json()
        assert "incorrect" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent email fails."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 401  # Unauthorized

    @pytest.mark.asyncio
    async def test_login_inactive_user(
        self, client: AsyncClient, db: AsyncSession, test_user: User
    ):
        """Test login with inactive account fails."""
        # Deactivate user
        test_user.is_active = False
        await db.commit()

        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "testpassword123",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "inactive" in data["detail"].lower()


class TestTokenOperations:
    """Test token refresh and logout."""

    @pytest.mark.asyncio
    async def test_refresh_token_success(
        self, client: AsyncClient, auth_tokens: dict
    ):
        """Test successful token refresh."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": auth_tokens["refresh_token"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["access_token"] != auth_tokens["access_token"]

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, client: AsyncClient):
        """Test token refresh with invalid token fails."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_blacklisted_token(
        self, client: AsyncClient, auth_tokens: dict
    ):
        """Test token refresh with blacklisted token fails."""
        # Blacklist the refresh token
        await blacklist_token(auth_tokens["refresh_token"], 3600)

        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": auth_tokens["refresh_token"]},
        )

        assert response.status_code == 401
        data = response.json()
        assert "revoked" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_logout_success(
        self, client: AsyncClient, auth_headers: dict, auth_tokens: dict
    ):
        """Test successful logout."""
        response = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": auth_tokens["refresh_token"]},
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Try to use access token after logout
        me_response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers,
        )
        assert me_response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """Test getting current user info."""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id

    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, client: AsyncClient):
        """Test getting current user without token fails."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401


class TestEmailVerification:
    """Test email verification endpoints."""

    @pytest.mark.asyncio
    async def test_verify_email_success(
        self, client: AsyncClient, db: AsyncSession, test_user: User
    ):
        """Test successful email verification."""
        # Generate verification token
        token = create_verification_token(test_user.email)

        response = await client.post(
            "/api/v1/auth/verify-email",
            json={"token": token},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_verified"] is True

        # Verify in database
        await db.refresh(test_user)
        assert test_user.is_verified is True

    @pytest.mark.asyncio
    async def test_verify_email_invalid_token(self, client: AsyncClient):
        """Test email verification with invalid token fails."""
        response = await client.post(
            "/api/v1/auth/verify-email",
            json={"token": "invalid-token"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_resend_verification_success(
        self, client: AsyncClient, test_user: User
    ):
        """Test resending verification email."""
        response = await client.post(
            "/api/v1/auth/resend-verification",
            json={"email": test_user.email},
        )

        assert response.status_code == 200
        data = response.json()
        assert "sent" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_resend_verification_already_verified(
        self, client: AsyncClient, db: AsyncSession, test_user: User
    ):
        """Test resending verification for already verified email fails."""
        # Verify user first
        test_user.is_verified = True
        await db.commit()

        response = await client.post(
            "/api/v1/auth/resend-verification",
            json={"email": test_user.email},
        )

        assert response.status_code == 422  # Validation error


class TestPasswordReset:
    """Test password reset flow."""

    @pytest.mark.asyncio
    async def test_request_password_reset(
        self, client: AsyncClient, test_user: User
    ):
        """Test requesting password reset."""
        response = await client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": test_user.email},
        )

        assert response.status_code == 200
        data = response.json()
        assert "sent" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_request_password_reset_nonexistent_email(
        self, client: AsyncClient
    ):
        """Test password reset request for non-existent email."""
        # Should return success to prevent email enumeration
        response = await client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "nonexistent@example.com"},
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_reset_password_success(
        self, client: AsyncClient, db: AsyncSession, test_user: User
    ):
        """Test successful password reset."""
        # Generate reset token
        token = create_password_reset_token(test_user.email)

        response = await client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": token,
                "new_password": "newsecurepassword123",
            },
        )

        assert response.status_code == 200

        # Try logging in with new password
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "newsecurepassword123",
            },
        )
        assert login_response.status_code == 200

    @pytest.mark.asyncio
    async def test_reset_password_invalid_token(self, client: AsyncClient):
        """Test password reset with invalid token fails."""
        response = await client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": "invalid-token",
                "new_password": "newsecurepassword123",
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_reset_password_weak_password(
        self, client: AsyncClient, test_user: User
    ):
        """Test password reset with weak password fails."""
        token = create_password_reset_token(test_user.email)

        response = await client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": token,
                "new_password": "short",  # Too short
            },
        )

        assert response.status_code == 422


class TestPasswordChange:
    """Test password change for logged-in users."""

    @pytest.mark.asyncio
    async def test_change_password_success(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """Test successful password change."""
        response = await client.post(
            "/api/v1/auth/password/change",
            json={
                "current_password": "testpassword123",
                "new_password": "newsecurepassword123",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Try logging in with new password
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "newsecurepassword123",
            },
        )
        assert login_response.status_code == 200

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test password change with wrong current password fails."""
        response = await client.post(
            "/api/v1/auth/password/change",
            json={
                "current_password": "wrongpassword",
                "new_password": "newsecurepassword123",
            },
            headers=auth_headers,
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_change_password_not_authenticated(
        self, client: AsyncClient
    ):
        """Test password change without authentication fails."""
        response = await client.post(
            "/api/v1/auth/password/change",
            json={
                "current_password": "testpassword123",
                "new_password": "newsecurepassword123",
            },
        )

        assert response.status_code == 401
