# Weight Coach - Backend Architecture Plan

> Comprehensive FastAPI backend architecture and design patterns
> Last Updated: 2025-11-18

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Layer Responsibilities](#layer-responsibilities)
3. [Directory Structure](#directory-structure)
4. [Architecture Patterns](#architecture-patterns)
5. [Core Modules](#core-modules)
6. [API Design](#api-design)
7. [Error Handling](#error-handling)
8. [Middleware Stack](#middleware-stack)
9. [Background Tasks](#background-tasks)
10. [Real-time Features](#real-time-features)
11. [File Upload Strategy](#file-upload-strategy)
12. [Security & Authentication](#security--authentication)
13. [Caching Strategy](#caching-strategy)
14. [Testing Strategy](#testing-strategy)
15. [Performance Optimization](#performance-optimization)
16. [Implementation Phases](#implementation-phases)

---

## Architecture Overview

### Design Philosophy

Weight Coach backend follows a **Layered Architecture** pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                         │
│            (Next.js Frontend, Mobile Apps)              │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP/WebSocket
┌─────────────────────▼───────────────────────────────────┐
│                 Presentation Layer                      │
│        (FastAPI Routes, WebSocket Handlers)             │
│  - Request validation (Pydantic)                        │
│  - Response serialization                               │
│  - HTTP status codes                                    │
└─────────────────────┬───────────────────────────────────┘
                      │ Dependency Injection
┌─────────────────────▼───────────────────────────────────┐
│                  Service Layer                          │
│              (Business Logic)                           │
│  - Domain logic                                         │
│  - Transaction management                               │
│  - External API integration (OpenAI)                    │
│  - Caching (Redis)                                      │
└─────────────────────┬───────────────────────────────────┘
                      │ Repository Pattern
┌─────────────────────▼───────────────────────────────────┐
│              Repository Layer                           │
│           (Data Access Logic)                           │
│  - CRUD operations                                      │
│  - Query building                                       │
│  - SQLAlchemy queries                                   │
└─────────────────────┬───────────────────────────────────┘
                      │ ORM
┌─────────────────────▼───────────────────────────────────┐
│               Database Layer                            │
│    (PostgreSQL, Redis, File Storage)                    │
└─────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Separation of Concerns**: Each layer has a single responsibility
2. **Dependency Injection**: Loose coupling through FastAPI's DI system
3. **Repository Pattern**: Abstract data access from business logic
4. **Service Pattern**: Encapsulate business logic and orchestration
5. **Async/Await**: Non-blocking I/O for all database and external API calls
6. **Type Safety**: Full type hints throughout codebase
7. **Testability**: Easy to mock and test each layer independently

---

## Layer Responsibilities

### 1. Presentation Layer (Routes)
**Location**: `app/api/v1/`

**Responsibilities**:
- HTTP request/response handling
- Input validation with Pydantic schemas
- Authentication/authorization checks
- Response formatting and status codes
- OpenAPI documentation

**What it DOES NOT do**:
- Business logic
- Database queries
- External API calls

**Example**:
```python
@router.post("/meals", response_model=MealFullResponse, status_code=201)
async def create_meal(
    meal_data: MealCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    meal_service: MealService = Depends(get_meal_service)
) -> MealFullResponse:
    """Create a new meal entry."""
    return await meal_service.create_meal(db, current_user.id, meal_data)
```

### 2. Service Layer
**Location**: `app/services/`

**Responsibilities**:
- Business logic and rules
- Transaction management
- Orchestrating multiple repositories
- External API integration (OpenAI, file storage)
- Caching logic
- Error handling and retries

**What it DOES NOT do**:
- Direct database queries (uses repositories)
- HTTP-specific logic (status codes, headers)

**Example**:
```python
class MealService:
    async def create_meal(
        self,
        db: AsyncSession,
        user_id: int,
        meal_data: MealCreate
    ) -> MealFullResponse:
        """
        Create meal with AI analysis.

        Business logic:
        1. Create meal record
        2. Process meal items
        3. Trigger AI analysis (background task)
        4. Return full meal with analysis
        """
        # Use repositories for data access
        meal = await self.meal_repo.create(db, user_id, meal_data)

        # Trigger AI analysis asynchronously
        if meal_data.input_method == "image":
            await self.ai_service.analyze_meal_image(meal.id, meal_data.image_url)

        return meal
```

### 3. Repository Layer
**Location**: `app/repositories/`

**Responsibilities**:
- CRUD operations
- Database queries (SQLAlchemy)
- Query optimization
- Filtering, sorting, pagination
- Data access abstraction

**What it DOES NOT do**:
- Business logic
- External API calls
- Transaction management (handled by service layer)

**Example**:
```python
class MealRepository:
    async def create(
        self,
        db: AsyncSession,
        user_id: int,
        meal_data: MealCreate
    ) -> Meal:
        """Create a new meal record."""
        meal = Meal(
            user_id=user_id,
            **meal_data.model_dump(exclude_unset=True)
        )
        db.add(meal)
        await db.flush()
        await db.refresh(meal)
        return meal

    async def get_user_meals(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Meal]:
        """Get user's meals with pagination and date filtering."""
        query = select(Meal).where(
            Meal.user_id == user_id,
            Meal.deleted_at.is_(None)
        )

        if start_date:
            query = query.where(Meal.consumed_at >= start_date)
        if end_date:
            query = query.where(Meal.consumed_at <= end_date)

        query = query.order_by(Meal.consumed_at.desc())
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()
```

---

## Directory Structure

### Complete Backend Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   │
│   ├── api/                       # Presentation layer
│   │   ├── __init__.py
│   │   ├── deps.py                # Common dependencies
│   │   └── v1/                    # API version 1
│   │       ├── __init__.py
│   │       ├── router.py          # Main API router
│   │       ├── auth.py            # Authentication endpoints
│   │       ├── users.py           # User management
│   │       ├── meals.py           # Meal logging
│   │       ├── inventory.py       # Inventory management
│   │       ├── recipes.py         # Recipe CRUD
│   │       ├── meal_plans.py      # Meal planning
│   │       ├── grocery_lists.py   # Shopping lists
│   │       ├── coach.py           # AI coaching
│   │       ├── analytics.py       # Progress tracking
│   │       └── uploads.py         # File upload endpoints
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py        # Authentication logic
│   │   ├── user_service.py        # User management
│   │   ├── meal_service.py        # Meal processing
│   │   ├── inventory_service.py   # Inventory logic
│   │   ├── recipe_service.py      # Recipe recommendations
│   │   ├── meal_plan_service.py   # Meal planning logic
│   │   ├── grocery_service.py     # Grocery list generation
│   │   ├── ai_service.py          # OpenAI integration
│   │   ├── nutrition_service.py   # Nutrition calculations
│   │   ├── file_service.py        # File upload/storage
│   │   └── notification_service.py # Real-time notifications
│   │
│   ├── repositories/              # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py                # Base repository with common CRUD
│   │   ├── user_repository.py
│   │   ├── meal_repository.py
│   │   ├── inventory_repository.py
│   │   ├── recipe_repository.py
│   │   ├── meal_plan_repository.py
│   │   └── grocery_repository.py
│   │
│   ├── models/                    # SQLAlchemy models (already created)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── meal.py
│   │   ├── inventory.py
│   │   ├── recipe.py
│   │   ├── meal_plan.py
│   │   ├── grocery.py
│   │   └── activity.py
│   │
│   ├── schemas/                   # Pydantic schemas (already created)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── meal.py
│   │   ├── inventory.py
│   │   ├── recipe.py
│   │   ├── meal_plan.py
│   │   ├── grocery.py
│   │   └── common.py              # Common schemas (pagination, etc.)
│   │
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py              # Settings (already created)
│   │   ├── security.py            # JWT, password hashing
│   │   ├── cache.py               # Redis caching utilities
│   │   ├── exceptions.py          # Custom exceptions
│   │   ├── logging.py             # Logging configuration
│   │   └── events.py              # Application events
│   │
│   ├── db/                        # Database (already created)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── database.py
│   │
│   ├── middleware/                # Custom middleware
│   │   ├── __init__.py
│   │   ├── error_handler.py       # Global error handling
│   │   ├── rate_limiter.py        # Rate limiting
│   │   ├── request_logger.py      # Request/response logging
│   │   └── cors.py                # CORS configuration
│   │
│   ├── tasks/                     # Background tasks
│   │   ├── __init__.py
│   │   ├── celery_app.py          # Celery configuration
│   │   ├── ai_tasks.py            # AI processing tasks
│   │   ├── email_tasks.py         # Email notifications
│   │   └── cleanup_tasks.py       # Data cleanup
│   │
│   ├── websocket/                 # WebSocket handlers
│   │   ├── __init__.py
│   │   ├── manager.py             # Connection manager
│   │   ├── handlers.py            # WebSocket message handlers
│   │   └── events.py              # Real-time event types
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── datetime.py            # Date/time utilities
│       ├── validators.py          # Custom validators
│       ├── formatters.py          # Data formatters
│       └── constants.py           # Application constants
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration
│   ├── test_api/                  # API endpoint tests
│   │   ├── test_auth.py
│   │   ├── test_meals.py
│   │   └── ...
│   ├── test_services/             # Service layer tests
│   │   ├── test_meal_service.py
│   │   └── ...
│   ├── test_repositories/         # Repository tests
│   │   ├── test_meal_repository.py
│   │   └── ...
│   └── fixtures/                  # Test fixtures and factories
│       ├── user_fixtures.py
│       └── meal_fixtures.py
│
├── alembic/                       # Database migrations (already created)
│   ├── versions/
│   └── env.py
│
├── scripts/                       # Utility scripts
│   ├── seed_data.py              # (already created as seed.py)
│   ├── create_admin.py           # Create admin user
│   └── clear_cache.py            # Clear Redis cache
│
├── requirements.txt               # (already created)
├── requirements-dev.txt           # Development dependencies
├── pyproject.toml                 # Project configuration
├── .env.example                   # (already created)
├── alembic.ini                    # (already created)
└── README.md                      # Backend-specific README
```

---

## Architecture Patterns

### 1. Repository Pattern

**Purpose**: Abstract data access logic from business logic

**Base Repository** (`app/repositories/base.py`):
```python
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """Get record by ID."""
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        obj_in: dict
    ) -> ModelType:
        """Create new record."""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: dict
    ) -> ModelType:
        """Update existing record."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: int) -> bool:
        """Delete record (hard delete)."""
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        db_obj = result.scalar_one_or_none()
        if db_obj:
            await db.delete(db_obj)
            await db.flush()
            return True
        return False

    async def soft_delete(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """Soft delete record (set deleted_at)."""
        db_obj = await self.get(db, id)
        if db_obj and hasattr(db_obj, 'soft_delete'):
            db_obj.soft_delete()
            await db.flush()
            await db.refresh(db_obj)
            return db_obj
        return None
```

**Specific Repository** (`app/repositories/meal_repository.py`):
```python
class MealRepository(BaseRepository[Meal]):
    """Meal-specific data access."""

    def __init__(self):
        super().__init__(Meal)

    async def get_user_meals_by_date(
        self,
        db: AsyncSession,
        user_id: int,
        date: date
    ) -> List[Meal]:
        """Get user's meals for specific date."""
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())

        result = await db.execute(
            select(Meal)
            .where(
                Meal.user_id == user_id,
                Meal.consumed_at.between(start, end),
                Meal.deleted_at.is_(None)
            )
            .order_by(Meal.consumed_at.desc())
        )
        return result.scalars().all()

    async def get_meals_with_analysis(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 10
    ) -> List[Meal]:
        """Get meals with AI analysis preloaded."""
        result = await db.execute(
            select(Meal)
            .options(selectinload(Meal.ai_analysis))
            .where(
                Meal.user_id == user_id,
                Meal.deleted_at.is_(None)
            )
            .order_by(Meal.consumed_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
```

### 2. Service Pattern

**Purpose**: Encapsulate business logic and orchestrate multiple repositories

**Service Layer** (`app/services/meal_service.py`):
```python
class MealService:
    """Meal-related business logic."""

    def __init__(
        self,
        meal_repo: MealRepository,
        ai_service: AIService,
        cache: CacheService
    ):
        self.meal_repo = meal_repo
        self.ai_service = ai_service
        self.cache = cache

    async def create_meal_with_analysis(
        self,
        db: AsyncSession,
        user_id: int,
        meal_data: MealCreate
    ) -> MealFullResponse:
        """
        Create meal and trigger AI analysis.

        Business logic:
        1. Validate meal data
        2. Create meal record
        3. Process meal items if provided
        4. Trigger AI analysis (async)
        5. Invalidate user's meal cache
        6. Return complete meal object
        """
        # Create meal
        meal = await self.meal_repo.create(
            db,
            {**meal_data.model_dump(), "user_id": user_id}
        )

        # Create meal items if provided
        if meal_data.items:
            await self._create_meal_items(db, meal.id, meal_data.items)

        # Trigger AI analysis asynchronously
        if meal_data.input_method == "image" and meal_data.image_url:
            # Background task will handle this
            await self.ai_service.queue_meal_image_analysis(
                meal.id,
                meal_data.image_url
            )
        elif meal_data.input_method == "voice" and meal_data.voice_transcript:
            await self.ai_service.queue_voice_analysis(
                meal.id,
                meal_data.voice_transcript
            )
        else:
            # Text input - analyze immediately
            analysis = await self.ai_service.analyze_meal_text(
                meal.name,
                meal.description
            )
            await self._save_analysis(db, meal.id, analysis)

        # Invalidate cache
        await self.cache.delete(f"user_meals:{user_id}")

        # Commit transaction
        await db.commit()

        # Return full meal with items and analysis
        return await self.get_meal_full(db, meal.id, user_id)

    async def get_user_daily_summary(
        self,
        db: AsyncSession,
        user_id: int,
        date: date
    ) -> DailySummaryResponse:
        """
        Get user's daily nutrition summary.

        Returns:
        - Total calories
        - Macro breakdown
        - Meal count
        - Goal progress
        """
        # Try cache first
        cache_key = f"daily_summary:{user_id}:{date}"
        cached = await self.cache.get(cache_key)
        if cached:
            return DailySummaryResponse.model_validate_json(cached)

        # Get meals for the day
        meals = await self.meal_repo.get_user_meals_by_date(db, user_id, date)

        # Calculate totals
        summary = self._calculate_summary(meals)

        # Get user's goals
        user_goal = await self.user_service.get_active_goal(db, user_id)
        if user_goal:
            summary.goal_progress = self._calculate_goal_progress(
                summary,
                user_goal
            )

        # Cache for 5 minutes
        await self.cache.set(
            cache_key,
            summary.model_dump_json(),
            expire=300
        )

        return summary
```

### 3. Dependency Injection

**Purpose**: Manage dependencies and promote loose coupling

**Dependencies** (`app/api/deps.py`):
```python
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import verify_token
from app.core.cache import get_cache
from app.repositories.user_repository import UserRepository
from app.repositories.meal_repository import MealRepository
from app.services.user_service import UserService
from app.services.meal_service import MealService
from app.services.ai_service import AIService
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Current user dependency
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user_repo = UserRepository()
    user = await user_repo.get(db, user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    return user

# Active user dependency (must be verified)
async def get_current_active_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current user who is active and verified."""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    return current_user

# Repository dependencies
def get_user_repository() -> UserRepository:
    return UserRepository()

def get_meal_repository() -> MealRepository:
    return MealRepository()

# Service dependencies
def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(user_repo)

def get_meal_service(
    meal_repo: MealRepository = Depends(get_meal_repository),
    ai_service: AIService = Depends(get_ai_service),
    cache = Depends(get_cache)
) -> MealService:
    return MealService(meal_repo, ai_service, cache)

def get_ai_service() -> AIService:
    return AIService()
```

---

## Core Modules

### 1. Authentication & Authorization

**Location**: `app/core/security.py`, `app/services/auth_service.py`

**Features**:
- JWT token generation and validation
- Password hashing (bcrypt)
- Refresh token mechanism
- Email verification
- Password reset flow

**Implementation**:
```python
# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Generate JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token."""
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
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)
```

**Auth Endpoints** (`app/api/v1/auth.py`):
```python
@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    """Register new user."""
    return await auth_service.register_user(db, user_data)

@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """Login user and return tokens."""
    return await auth_service.authenticate_user(db, credentials)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """Refresh access token using refresh token."""
    return await auth_service.refresh_access_token(refresh_token)

@router.post("/verify-email/{token}")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """Verify user email with token."""
    await auth_service.verify_user_email(db, token)
    return {"message": "Email verified successfully"}
```

### 2. AI Integration Module

**Location**: `app/services/ai_service.py`

**Features**:
- GPT-4 nutrition analysis
- Whisper voice transcription
- Vision API for meal image recognition
- Personalized coaching recommendations
- Retry logic with exponential backoff
- Response caching

**Implementation**:
```python
class AIService:
    """OpenAI API integration service."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.cache = CacheService()

    async def analyze_meal_text(
        self,
        meal_name: str,
        description: Optional[str] = None
    ) -> NutritionAnalysis:
        """
        Analyze meal using GPT-4.

        Returns nutrition breakdown and recommendations.
        """
        # Check cache first
        cache_key = f"meal_analysis:{meal_name}:{description}"
        cached = await self.cache.get(cache_key)
        if cached:
            return NutritionAnalysis.model_validate_json(cached)

        # Build prompt
        prompt = self._build_nutrition_prompt(meal_name, description)

        # Call GPT-4 with retry logic
        response = await self._call_gpt4_with_retry(prompt)

        # Parse response
        analysis = self._parse_nutrition_response(response)

        # Cache for 24 hours
        await self.cache.set(
            cache_key,
            analysis.model_dump_json(),
            expire=86400
        )

        return analysis

    async def analyze_meal_image(
        self,
        image_url: str
    ) -> MealImageAnalysis:
        """
        Analyze meal from image using Vision API.

        Identifies food items and estimates portions.
        """
        # Use GPT-4 Vision
        response = await self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Identify all food items in this meal and estimate portion sizes. Provide nutrition information."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }
            ],
            max_tokens=1000
        )

        return self._parse_vision_response(response)

    async def transcribe_voice(
        self,
        audio_file_path: str
    ) -> str:
        """
        Transcribe voice recording using Whisper.

        Returns text transcription.
        """
        with open(audio_file_path, "rb") as audio_file:
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )

        return transcript

    async def get_personalized_recommendations(
        self,
        user_profile: UserProfile,
        user_goal: UserGoal,
        recent_meals: List[Meal]
    ) -> CoachingRecommendations:
        """
        Get personalized coaching recommendations based on user data.

        Analyzes eating patterns and suggests improvements.
        """
        # Build context from user data
        context = self._build_coaching_context(
            user_profile,
            user_goal,
            recent_meals
        )

        # Call GPT-4 for recommendations
        prompt = f"""
        As a nutrition coach, provide personalized recommendations for this user:

        Profile: {context['profile']}
        Goal: {context['goal']}
        Recent eating patterns: {context['meals']}

        Provide:
        1. Overall assessment
        2. 3-5 specific actionable recommendations
        3. Meal suggestions for tomorrow
        """

        response = await self._call_gpt4_with_retry(prompt)
        return self._parse_coaching_response(response)

    async def _call_gpt4_with_retry(
        self,
        prompt: str,
        max_retries: int = 3
    ) -> str:
        """Call GPT-4 with exponential backoff retry."""
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=settings.OPENAI_MAX_TOKENS,
                    temperature=settings.OPENAI_TEMPERATURE
                )
                return response.choices[0].message.content
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt  # Exponential backoff
                await asyncio.sleep(wait_time)
```

### 3. File Upload Module

**Location**: `app/services/file_service.py`, `app/api/v1/uploads.py`

**Features**:
- Image upload for meals
- File validation (size, type)
- S3/cloud storage integration
- Image compression
- Temporary file cleanup

**Implementation**:
```python
# app/services/file_service.py
class FileService:
    """File upload and storage service."""

    async def upload_meal_image(
        self,
        file: UploadFile,
        user_id: int
    ) -> str:
        """
        Upload meal image to storage.

        Returns:
            Public URL of uploaded image
        """
        # Validate file
        self._validate_image(file)

        # Generate unique filename
        filename = self._generate_filename(file.filename, user_id)

        # Compress image
        compressed = await self._compress_image(file)

        # Upload to S3 (or local storage in dev)
        url = await self._upload_to_storage(compressed, filename)

        return url

    def _validate_image(self, file: UploadFile) -> None:
        """Validate image file."""
        # Check file type
        if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {settings.ALLOWED_IMAGE_TYPES}"
            )

        # Check file size
        if file.size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max: {settings.MAX_UPLOAD_SIZE} bytes"
            )

    async def _compress_image(
        self,
        file: UploadFile,
        max_size: tuple = (1024, 1024)
    ) -> BytesIO:
        """Compress image to reduce size."""
        from PIL import Image

        # Read image
        image = Image.open(file.file)

        # Resize if needed
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save compressed
        output = BytesIO()
        image.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)

        return output

# app/api/v1/uploads.py
@router.post("/meals/image")
async def upload_meal_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
) -> dict:
    """Upload meal image."""
    url = await file_service.upload_meal_image(file, current_user.id)
    return {"url": url}
```

### 4. WebSocket Module (Real-time Updates)

**Location**: `app/websocket/`

**Features**:
- Real-time meal analysis updates
- Progress notifications
- Live coaching feedback
- Connection management

**Implementation**:
```python
# app/websocket/manager.py
class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        """Accept and store connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        """Remove connection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, user_id: int, message: dict):
        """Send message to specific user."""
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

    async def broadcast(self, message: dict):
        """Broadcast to all connected clients."""
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()

# app/websocket/handlers.py
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    token: str = Query(...)
):
    """WebSocket endpoint for real-time updates."""
    # Verify token
    payload = verify_token(token)
    if not payload or payload.get("sub") != user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(user_id, websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_json()

            # Handle incoming messages
            if data.get("type") == "ping":
                await manager.send_personal_message(
                    user_id,
                    {"type": "pong"}
                )
    except WebSocketDisconnect:
        manager.disconnect(user_id)

# Usage: Send real-time analysis update
async def notify_meal_analysis_complete(user_id: int, meal_id: int, analysis: dict):
    """Notify user when AI analysis is complete."""
    await manager.send_personal_message(user_id, {
        "type": "meal_analysis_complete",
        "meal_id": meal_id,
        "analysis": analysis
    })
```

### 5. Background Tasks Module

**Location**: `app/tasks/`

**Options**:
- **Celery** (for distributed tasks, production)
- **FastAPI BackgroundTasks** (simpler, for hackathon MVP)

**Features**:
- Async AI processing
- Email notifications
- Data cleanup
- Scheduled tasks (expiration notifications)

**Implementation (FastAPI BackgroundTasks for MVP)**:
```python
# app/api/v1/meals.py
@router.post("/meals", response_model=MealResponse, status_code=201)
async def create_meal(
    meal_data: MealCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    meal_service: MealService = Depends(get_meal_service),
    ai_service: AIService = Depends(get_ai_service)
) -> MealResponse:
    """Create meal with async AI analysis."""
    # Create meal
    meal = await meal_service.create_meal(db, current_user.id, meal_data)

    # Queue AI analysis in background
    background_tasks.add_task(
        process_meal_analysis,
        meal.id,
        meal_data,
        current_user.id
    )

    return meal

async def process_meal_analysis(
    meal_id: int,
    meal_data: MealCreate,
    user_id: int
):
    """Background task: Process AI analysis."""
    async with AsyncSessionLocal() as db:
        try:
            # Run AI analysis
            analysis = await ai_service.analyze_meal(meal_data)

            # Save to database
            ai_analysis = AIAnalysis(
                meal_id=meal_id,
                analysis=analysis.text,
                recommendations=analysis.recommendations,
                nutrition_breakdown=analysis.nutrition,
                confidence_score=analysis.confidence,
                model_version="gpt-4"
            )
            db.add(ai_analysis)
            await db.commit()

            # Notify user via WebSocket
            await notify_meal_analysis_complete(
                user_id,
                meal_id,
                analysis.model_dump()
            )
        except Exception as e:
            logger.error(f"Failed to analyze meal {meal_id}: {e}")
```

**Celery Setup (for production)**:
```python
# app/tasks/celery_app.py
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "weight_coach",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# app/tasks/ai_tasks.py
@celery_app.task(bind=True, max_retries=3)
def analyze_meal_task(self, meal_id: int, meal_data: dict):
    """Celery task for AI analysis."""
    try:
        # Process analysis
        ai_service = AIService()
        analysis = ai_service.analyze_meal(meal_data)

        # Save to database
        # ... (similar to above)

        return {"status": "success", "meal_id": meal_id}
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
```

---

## API Design

### REST API Organization

**Base URL**: `/api/v1`

**Endpoint Structure**:
```
/api/v1
├── /auth
│   ├── POST /register          # Register new user
│   ├── POST /login             # Login
│   ├── POST /refresh           # Refresh token
│   ├── POST /logout            # Logout
│   ├── POST /forgot-password   # Request password reset
│   ├── POST /reset-password    # Reset password
│   └── GET  /verify-email/{token}  # Verify email
│
├── /users
│   ├── GET    /me              # Get current user
│   ├── PATCH  /me              # Update current user
│   ├── DELETE /me              # Delete account
│   ├── GET    /me/profile      # Get user profile
│   ├── PUT    /me/profile      # Update profile
│   ├── GET    /me/goals        # Get user goals
│   ├── POST   /me/goals        # Create goal
│   ├── PATCH  /me/goals/{id}   # Update goal
│   └── DELETE /me/goals/{id}   # Delete goal
│
├── /meals
│   ├── GET    /                # List user's meals
│   ├── POST   /                # Create meal
│   ├── GET    /{id}            # Get meal details
│   ├── PATCH  /{id}            # Update meal
│   ├── DELETE /{id}            # Delete meal
│   ├── GET    /daily-summary   # Get day summary
│   ├── GET    /weekly-summary  # Get week summary
│   └── POST   /{id}/analyze    # Trigger re-analysis
│
├── /inventory
│   ├── GET    /                # List inventory items
│   ├── POST   /                # Add item
│   ├── GET    /{id}            # Get item details
│   ├── PATCH  /{id}            # Update item
│   ├── DELETE /{id}            # Remove item
│   ├── GET    /expiring-soon   # Get expiring items
│   └── GET    /categories      # List food categories
│
├── /recipes
│   ├── GET    /                # Browse recipes
│   ├── POST   /                # Create recipe
│   ├── GET    /{id}            # Get recipe details
│   ├── PATCH  /{id}            # Update recipe
│   ├── DELETE /{id}            # Delete recipe
│   ├── GET    /saved           # Get saved recipes
│   ├── POST   /{id}/save       # Save recipe
│   ├── DELETE /{id}/save       # Unsave recipe
│   ├── POST   /{id}/rate       # Rate recipe
│   └── GET    /recommendations # Get AI recommendations
│
├── /meal-plans
│   ├── GET    /                # List meal plans
│   ├── POST   /                # Create meal plan
│   ├── GET    /{id}            # Get plan details
│   ├── PATCH  /{id}            # Update plan
│   ├── DELETE /{id}            # Delete plan
│   ├── GET    /{id}/items      # Get plan items
│   ├── POST   /{id}/items      # Add item to plan
│   ├── PATCH  /{id}/items/{item_id}  # Update plan item
│   ├── DELETE /{id}/items/{item_id}  # Remove plan item
│   └── POST   /{id}/generate-list    # Generate grocery list
│
├── /grocery-lists
│   ├── GET    /                # List grocery lists
│   ├── POST   /                # Create list
│   ├── GET    /{id}            # Get list details
│   ├── PATCH  /{id}            # Update list
│   ├── DELETE /{id}            # Delete list
│   ├── GET    /{id}/items      # Get list items
│   ├── POST   /{id}/items      # Add item
│   ├── PATCH  /{id}/items/{item_id}  # Update item
│   ├── DELETE /{id}/items/{item_id}  # Remove item
│   └── POST   /{id}/items/{item_id}/check  # Check/uncheck item
│
├── /coach
│   ├── GET    /recommendations # Get personalized recommendations
│   ├── POST   /analyze         # Analyze eating patterns
│   ├── GET    /progress        # Get progress insights
│   └── POST   /ask             # Ask nutrition question
│
├── /analytics
│   ├── GET    /nutrition       # Nutrition trends
│   ├── GET    /weight          # Weight progress
│   ├── GET    /macros          # Macro distribution
│   └── GET    /streaks         # Logging streaks
│
└── /uploads
    ├── POST /meal-image        # Upload meal image
    ├── POST /voice-recording   # Upload voice
    └── POST /profile-picture   # Upload profile pic
```

### Common Query Parameters

**Pagination**:
- `skip` (default: 0)
- `limit` (default: 20, max: 100)

**Filtering**:
- `start_date`, `end_date` (for date range)
- `meal_type` (breakfast/lunch/dinner/snack)
- `category_id` (for inventory/recipes)

**Sorting**:
- `sort_by` (field name)
- `order` (asc/desc)

**Example**:
```
GET /api/v1/meals?start_date=2025-01-01&end_date=2025-01-31&meal_type=breakfast&limit=50
```

### Response Format

**Success Response**:
```json
{
  "data": { /* resource data */ },
  "message": "Success message"
}
```

**List Response** (with pagination):
```json
{
  "data": [ /* array of resources */ ],
  "meta": {
    "total": 100,
    "skip": 0,
    "limit": 20,
    "has_more": true
  }
}
```

**Error Response**:
```json
{
  "detail": "Error message",
  "error_code": "MEAL_NOT_FOUND",
  "status_code": 404
}
```

---

## Error Handling

### Custom Exception Classes

**Location**: `app/core/exceptions.py`

```python
class BaseAPIException(Exception):
    """Base exception for API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR"
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class NotFoundException(BaseAPIException):
    """Resource not found."""
    def __init__(self, resource: str, id: int):
        super().__init__(
            message=f"{resource} with id {id} not found",
            status_code=404,
            error_code=f"{resource.upper()}_NOT_FOUND"
        )

class UnauthorizedException(BaseAPIException):
    """Unauthorized access."""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED"
        )

class ForbiddenException(BaseAPIException):
    """Forbidden access."""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN"
        )

class ValidationException(BaseAPIException):
    """Validation error."""
    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Validation error for {field}: {message}",
            status_code=422,
            error_code="VALIDATION_ERROR"
        )

class RateLimitException(BaseAPIException):
    """Rate limit exceeded."""
    def __init__(self):
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED"
        )
```

### Global Error Handler

**Location**: `app/middleware/error_handler.py`

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import BaseAPIException
from app.core.logging import logger

async def api_exception_handler(request: Request, exc: BaseAPIException):
    """Handle custom API exceptions."""
    logger.error(
        f"API Error: {exc.error_code} - {exc.message}",
        extra={"path": request.url.path, "method": request.method}
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "status_code": exc.status_code
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(f"Validation error: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "errors": errors
        }
    )

async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors."""
    logger.error(f"Database error: {str(exc)}")

    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": "Database integrity error",
                "error_code": "INTEGRITY_ERROR"
            }
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_code": "DATABASE_ERROR"
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.exception(f"Unexpected error: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )

# Register in main.py
def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(BaseAPIException, api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
```

---

## Middleware Stack

### Execution Order

```
Request
  ↓
1. CORS Middleware (allow cross-origin requests)
  ↓
2. Request Logger (log incoming requests)
  ↓
3. Rate Limiter (prevent abuse)
  ↓
4. Authentication (validate JWT)
  ↓
5. Route Handler (your endpoint)
  ↓
6. Error Handler (catch exceptions)
  ↓
7. Response Logger (log outgoing responses)
  ↓
Response
```

### Middleware Implementations

**1. CORS Middleware** (`app/middleware/cors.py`):
```python
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app: FastAPI):
    """Configure CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Page-Count"]
    )
```

**2. Request/Response Logger** (`app/middleware/request_logger.py`):
```python
import time
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses."""

    async def dispatch(self, request: Request, call_next):
        # Log request
        start_time = time.time()

        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host,
                "user_agent": request.headers.get("user-agent")
            }
        )

        # Process request
        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time

        logger.info(
            f"Response: {response.status_code} ({process_time:.3f}s)",
            extra={
                "status_code": response.status_code,
                "process_time": process_time,
                "path": request.url.path
            }
        )

        # Add custom headers
        response.headers["X-Process-Time"] = str(process_time)

        return response
```

**3. Rate Limiter** (`app/middleware/rate_limiter.py`):
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"]
)

def setup_rate_limiter(app: FastAPI):
    """Configure rate limiting."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Usage in routes:
@router.post("/meals")
@limiter.limit("10/minute")  # Specific rate limit
async def create_meal(...):
    pass
```

---

## Caching Strategy

**Location**: `app/core/cache.py`

**What to Cache**:
- User profiles (1 hour)
- Daily summaries (5 minutes)
- Recipe search results (30 minutes)
- AI analysis results (24 hours)
- Public recipes (1 hour)

**Implementation**:
```python
import json
from typing import Optional, Any
from redis.asyncio import Redis
from app.core.config import settings

class CacheService:
    """Redis caching service."""

    def __init__(self):
        self.redis: Optional[Redis] = None

    async def connect(self):
        """Connect to Redis."""
        self.redis = await Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if not self.redis:
            return None
        return await self.redis.get(key)

    async def set(
        self,
        key: str,
        value: str,
        expire: int = 3600
    ) -> bool:
        """Set value in cache with expiration."""
        if not self.redis:
            return False
        return await self.redis.setex(key, expire, value)

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.redis:
            return False
        return await self.redis.delete(key) > 0

    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern."""
        if not self.redis:
            return 0
        keys = await self.redis.keys(pattern)
        if keys:
            return await self.redis.delete(*keys)
        return 0

# Usage in services
async def get_user_profile(
    db: AsyncSession,
    user_id: int,
    cache: CacheService
) -> UserProfile:
    """Get user profile with caching."""
    # Try cache first
    cache_key = f"user_profile:{user_id}"
    cached = await cache.get(cache_key)

    if cached:
        return UserProfile.model_validate_json(cached)

    # Get from database
    profile = await user_repo.get_profile(db, user_id)

    # Cache for 1 hour
    await cache.set(
        cache_key,
        profile.model_dump_json(),
        expire=3600
    )

    return profile
```

---

## Testing Strategy

### Test Pyramid

```
        /\
       /  \      E2E Tests (5%)
      /____\     - Full user flows
     /      \    - API integration
    /________\   Integration Tests (20%)
   /          \  - Service layer with DB
  /____________\ - Repository tests
 /              \ Unit Tests (75%)
/______________/  - Pure functions
                  - Business logic
```

### Test Organization

**1. Unit Tests** (`tests/test_services/`):
```python
# tests/test_services/test_meal_service.py
import pytest
from unittest.mock import Mock, AsyncMock
from app.services.meal_service import MealService

@pytest.mark.asyncio
async def test_create_meal_with_text_input():
    """Test meal creation with text input."""
    # Arrange
    mock_repo = AsyncMock()
    mock_ai = AsyncMock()
    mock_cache = AsyncMock()
    service = MealService(mock_repo, mock_ai, mock_cache)

    meal_data = MealCreate(
        name="Chicken Salad",
        input_method="text",
        description="Grilled chicken with mixed greens"
    )

    # Act
    result = await service.create_meal(mock_db, 1, meal_data)

    # Assert
    mock_repo.create.assert_called_once()
    mock_ai.analyze_meal_text.assert_called_once()
    assert result.name == "Chicken Salad"
```

**2. Integration Tests** (`tests/test_api/`):
```python
# tests/test_api/test_meals.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_meal_endpoint(
    client: AsyncClient,
    auth_headers: dict,
    db_session
):
    """Test meal creation endpoint."""
    response = await client.post(
        "/api/v1/meals",
        json={
            "name": "Chicken Salad",
            "meal_type": "lunch",
            "consumed_at": "2025-01-15T12:30:00",
            "input_method": "text"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Chicken Salad"
    assert data["meal_type"] == "lunch"

    # Verify in database
    meal = await db_session.get(Meal, data["id"])
    assert meal is not None
    assert meal.user_id == 1  # From auth_headers
```

**3. Fixtures** (`tests/conftest.py`):
```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.main import app
from app.db.database import get_db
from app.core.security import create_access_token

# Test database
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/weight_coach_test"

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL)
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(test_engine):
    """Create database session for tests."""
    async with AsyncSession(test_engine) as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session):
    """Create test client."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def auth_headers():
    """Create authentication headers for tests."""
    token = create_access_token({"sub": 1})
    return {"Authorization": f"Bearer {token}"}
```

---

## Performance Optimization

### 1. Database Query Optimization

**Use eager loading**:
```python
# Bad: N+1 queries
meals = await db.execute(select(Meal).where(Meal.user_id == user_id))
for meal in meals:
    # This creates separate query for each meal
    items = meal.meal_items

# Good: Single query with join
meals = await db.execute(
    select(Meal)
    .options(selectinload(Meal.meal_items))
    .where(Meal.user_id == user_id)
)
```

**Use pagination**:
```python
# Always limit query results
query = query.offset(skip).limit(min(limit, 100))
```

**Use indexes** (already defined in models):
```python
# Composite index for common queries
Index('idx_meals_user_date', 'user_id', 'consumed_at')
```

### 2. Caching

**Cache expensive operations**:
- AI analysis results (24 hours)
- Daily summaries (5 minutes)
- User profiles (1 hour)
- Recipe search (30 minutes)

**Cache invalidation**:
```python
# Invalidate cache when data changes
async def create_meal(...):
    meal = await meal_repo.create(...)

    # Invalidate user's meal cache
    await cache.delete(f"user_meals:{user_id}")
    await cache.delete(f"daily_summary:{user_id}:*")

    return meal
```

### 3. Async/Await

**Use async for all I/O**:
```python
# Database queries
async def get_meal(...):
    result = await db.execute(...)

# External APIs
async def analyze_with_ai(...):
    response = await openai_client.chat.completions.create(...)

# File operations
async def save_file(...):
    async with aiofiles.open(...) as f:
        await f.write(...)
```

### 4. Connection Pooling

**Database pool** (already configured):
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,          # Number of connections in pool
    max_overflow=20,       # Additional connections when pool full
    pool_pre_ping=True     # Verify connection before using
)
```

---

## Implementation Phases

### Phase 1: MVP Core (Days 1-2)
**Priority: High - Must have for demo**

**Week 1, Days 1-2**:
1. ✅ Complete authentication system
   - JWT token generation/validation
   - User registration/login
   - Password hashing

2. ✅ Basic meal logging
   - Create/read/update/delete meals
   - Text input support
   - Basic validation

3. ✅ User profile management
   - CRUD operations for profiles
   - Goal setting

4. ✅ Simple AI integration
   - Text-based meal analysis
   - Basic nutrition estimation

**Deliverable**: Users can sign up, log meals via text, and get basic AI feedback

---

### Phase 2: Enhanced Features (Days 3-4)
**Priority: Medium - Impressive for demo**

**Week 1, Days 3-4**:
1. ✅ File upload system
   - Image upload for meals
   - S3 or local storage
   - Image compression

2. ✅ Advanced AI features
   - GPT-4 Vision for meal images
   - Whisper for voice input
   - Personalized coaching

3. ✅ Inventory management
   - CRUD operations
   - Expiration tracking
   - Low stock alerts

4. ✅ Recipe system
   - Recipe CRUD
   - Ingredients and instructions
   - Save/favorite functionality

**Deliverable**: Full-featured meal logging with AI, inventory, and recipes

---

### Phase 3: Planning & Lists (Day 5)
**Priority: Medium - Nice to have**

**Week 1, Day 5**:
1. ✅ Meal planning
   - Create weekly plans
   - Schedule recipes
   - Track completion

2. ✅ Grocery lists
   - Manual and auto-generated lists
   - Check off items
   - Category organization

3. ✅ Background tasks
   - Async AI processing
   - Email notifications

**Deliverable**: Complete planning and shopping features

---

### Phase 4: Real-time & Analytics (Day 6)
**Priority: Low - Polish for presentation**

**Week 1, Day 6**:
1. ✅ WebSocket integration
   - Real-time analysis updates
   - Live notifications

2. ✅ Analytics endpoints
   - Nutrition trends
   - Progress charts
   - Streak tracking

3. ✅ Performance optimization
   - Query optimization
   - Caching implementation
   - Rate limiting

**Deliverable**: Real-time features and analytics dashboard

---

### Phase 5: Testing & Documentation (Day 7)
**Priority: High - Production ready**

**Week 1, Day 7**:
1. ✅ Unit tests
   - Service layer tests
   - Repository tests
   - 60%+ coverage

2. ✅ Integration tests
   - API endpoint tests
   - E2E flows

3. ✅ API documentation
   - OpenAPI/Swagger complete
   - Example requests/responses
   - Error code documentation

4. ✅ Deployment preparation
   - Environment setup
   - Railway configuration
   - Monitoring setup

**Deliverable**: Tested, documented, deployment-ready backend

---

## Next Steps

Once this architecture plan is approved, implementation will proceed in this order:

1. **Core Setup** (1 day)
   - Main app initialization
   - Middleware setup
   - Error handling
   - Base repository
   - Dependencies

2. **Authentication** (1 day)
   - Security module
   - Auth service
   - Auth routes
   - JWT implementation

3. **Meal Management** (2 days)
   - Meal repository
   - Meal service
   - Meal routes
   - AI service integration

4. **Additional Features** (2 days)
   - Inventory, recipes, plans
   - File uploads
   - Background tasks

5. **Real-time & Polish** (1 day)
   - WebSocket
   - Analytics
   - Performance optimization

6. **Testing** (1 day)
   - Unit tests
   - Integration tests
   - Documentation

**Total**: 7-8 days for complete backend implementation

---

## Questions & Considerations

### Decision Points

1. **Background Tasks**:
   - FastAPI BackgroundTasks (simple, good for MVP)
   - Celery (distributed, production-ready)
   - **Recommendation**: Start with BackgroundTasks, migrate to Celery if needed

2. **File Storage**:
   - Local storage (development)
   - S3/CloudFlare R2 (production)
   - **Recommendation**: Abstract with FileService, easy to swap

3. **WebSocket**:
   - Native FastAPI WebSocket
   - Socket.IO
   - **Recommendation**: FastAPI WebSocket (simpler, fewer dependencies)

4. **Rate Limiting**:
   - slowapi (Redis-backed)
   - Custom middleware
   - **Recommendation**: slowapi for ease of use

5. **Testing**:
   - pytest-asyncio for async tests
   - httpx for API tests
   - **Recommendation**: Both, well-established

### Open Questions

1. Should we implement admin panel endpoints?
2. Do we need user roles (admin, premium, free)?
3. Should we support social auth (Google, Facebook)?
4. Do we need email verification for MVP?
5. Should we implement analytics tracking from day 1?

---

**This architecture provides**:
- ✅ Clear separation of concerns
- ✅ Scalable and maintainable structure
- ✅ Type-safe throughout
- ✅ Easy to test
- ✅ Ready for production deployment
- ✅ Hackathon-friendly (can implement incrementally)
