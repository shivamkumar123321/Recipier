"""
Pytest configuration and fixtures for testing.

Provides:
- Test database setup
- Test client
- Test user fixtures
- Authentication fixtures
"""

import asyncio
from typing import AsyncGenerator, Dict

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.cache import close_redis, get_redis
from app.core.security import create_access_token, get_password_hash
from app.db.base import Base
from app.db.database import get_db
from app.main import app
from app.models.user import User
from app.repositories.user_repository import user_repository

# Test database URL (use separate test database)
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/weight_coach_test"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,  # Disable connection pooling for tests
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""

    # Override get_db dependency to use test database
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    # Initialize Redis for tests
    try:
        await get_redis()
    except Exception:
        pass  # Redis may not be available in test environment

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client

    # Clean up
    app.dependency_overrides.clear()

    # Close Redis connection
    try:
        await close_redis()
    except Exception:
        pass


@pytest_asyncio.fixture(scope="function")
async def test_user(db: AsyncSession) -> User:
    """Create a test user."""
    user_data = {
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword123"),
        "is_active": True,
        "is_verified": False,
    }

    user = await user_repository.create(db, user_data)
    await db.commit()
    await db.refresh(user)

    return user


@pytest_asyncio.fixture(scope="function")
async def verified_user(db: AsyncSession) -> User:
    """Create a verified test user."""
    user_data = {
        "email": "verified@example.com",
        "hashed_password": get_password_hash("testpassword123"),
        "is_active": True,
        "is_verified": True,
    }

    user = await user_repository.create(db, user_data)
    await db.commit()
    await db.refresh(user)

    return user


@pytest_asyncio.fixture(scope="function")
async def admin_user(db: AsyncSession) -> User:
    """Create an admin test user."""
    user_data = {
        "email": "admin@example.com",
        "hashed_password": get_password_hash("testpassword123"),
        "is_active": True,
        "is_verified": True,
        "is_superuser": True,
    }

    user = await user_repository.create(db, user_data)
    await db.commit()
    await db.refresh(user)

    return user


@pytest_asyncio.fixture(scope="function")
async def auth_tokens(test_user: User) -> Dict[str, str]:
    """Generate authentication tokens for test user."""
    from app.core.security import create_refresh_token

    access_token = create_access_token({"sub": test_user.id})
    refresh_token = create_refresh_token({"sub": test_user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@pytest_asyncio.fixture(scope="function")
async def auth_headers(auth_tokens: Dict[str, str]) -> Dict[str, str]:
    """Generate authorization headers for test requests."""
    return {
        "Authorization": f"Bearer {auth_tokens['access_token']}",
    }


@pytest_asyncio.fixture(scope="function")
async def verified_auth_headers(verified_user: User) -> Dict[str, str]:
    """Generate authorization headers for verified user."""
    access_token = create_access_token({"sub": verified_user.id})

    return {
        "Authorization": f"Bearer {access_token}",
    }


@pytest_asyncio.fixture(scope="function")
async def admin_auth_headers(admin_user: User) -> Dict[str, str]:
    """Generate authorization headers for admin user."""
    access_token = create_access_token({"sub": admin_user.id})

    return {
        "Authorization": f"Bearer {access_token}",
    }


# Utility fixtures
@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Mocked AI response for testing",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        },
    }


@pytest.fixture
def sample_meal_data():
    """Sample meal data for testing."""
    return {
        "name": "Chicken Salad",
        "description": "Grilled chicken with mixed greens",
        "meal_type": "lunch",
        "consumed_at": "2025-11-18T12:00:00Z",
    }


@pytest.fixture
def sample_nutrition_data():
    """Sample nutrition data for testing."""
    return {
        "calories": 350.0,
        "protein_g": 35.0,
        "carbs_g": 20.0,
        "fat_g": 15.0,
        "fiber_g": 5.0,
        "sodium_mg": 450.0,
    }
