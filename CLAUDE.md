# Weight Coach - Project Documentation

> **AI-Powered Nutrition Coach for Hackathon**
> Last Updated: 2025-11-18

## 📋 Project Overview

Weight Coach is an AI-powered nutrition coaching web application designed to help users track their meals, get personalized nutrition advice, and achieve their health goals. The app leverages OpenAI's GPT-4 for intelligent coaching, Whisper for voice input, and Vision for food image recognition.

### Core Features
- **Meal Logging**: Voice, text, or image-based meal entry
- **AI Nutrition Analysis**: Real-time nutritional breakdown and insights
- **Personalized Coaching**: Tailored advice based on user goals and history
- **Progress Tracking**: Visual dashboards for calories, macros, and weight trends
- **Smart Recommendations**: Meal suggestions and dietary guidance

### Target Users
- Individuals tracking weight loss/gain goals
- Health-conscious users seeking nutritional guidance
- People looking for convenient meal logging via voice/photo

---

## 🏗️ Architecture

### System Design
```
┌─────────────────┐
│   Next.js App   │  (Vercel)
│   Frontend      │
└────────┬────────┘
         │ REST API / WebSocket
         ↓
┌─────────────────┐
│  FastAPI        │  (Railway)
│  Backend        │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┬───────────┐
    ↓          ↓          ↓           ↓
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Postgres│ │ Redis  │ │OpenAI  │ │External│
│   DB   │ │ Cache  │ │  API   │ │  APIs  │
└────────┘ └────────┘ └────────┘ └────────┘
```

### Data Flow
1. User inputs meal (text/voice/image) → Frontend
2. Frontend sends to FastAPI backend
3. Backend processes with OpenAI API
4. Results cached in Redis, stored in PostgreSQL
5. Real-time updates sent back to frontend

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.x (strict mode)
- **Styling**: Tailwind CSS 4.x (using CSS variables and @theme)
- **UI Components**: shadcn/ui (customized with design tokens)
- **State Management**: Zustand (global), React Query (server state)
- **Forms**: React Hook Form + Zod validation
- **HTTP Client**: Fetch API (via custom hooks)
- **Deployment**: Vercel

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+ (with type hints)
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.x
- **Caching**: Redis 7+
- **Migrations**: Alembic
- **Authentication**: JWT tokens
- **Deployment**: Railway

### AI Services
- **GPT-4**: Nutrition analysis and coaching
- **Whisper**: Speech-to-text for voice input
- **Vision (GPT-4V)**: Food image recognition
- **API Client**: OpenAI Python SDK

### DevOps & Tools
- **Version Control**: Git
- **Package Management**: npm (frontend), pip/poetry (backend)
- **Environment**: Docker (optional for local dev)
- **CI/CD**: GitHub Actions (if needed)
- **Monitoring**: Vercel Analytics, Railway logs

---

## 📁 Project Structure

```
weight-coach/
├── CLAUDE.md                  # This file - project memory
├── README.md                  # User-facing documentation
├── .gitignore                 # Git ignore rules
│
├── frontend/                  # Next.js application
│   ├── src/
│   │   ├── app/              # App Router pages
│   │   │   ├── (auth)/       # Authentication routes (layout group)
│   │   │   ├── (dashboard)/  # Dashboard routes (layout group)
│   │   │   ├── layout.tsx    # Root layout
│   │   │   └── globals.css   # Global styles & Tailwind config
│   │   │
│   │   ├── components/       # React components
│   │   │   ├── ui/           # shadcn/ui components
│   │   │   ├── layout/       # Layout components (Header, Sidebar)
│   │   │   ├── forms/        # Form components
│   │   │   ├── features/     # Feature-specific components
│   │   │   └── shared/       # Shared/common components
│   │   │
│   │   ├── lib/              # Utilities and helpers
│   │   │   ├── api.ts        # API client
│   │   │   ├── utils.ts      # General utilities
│   │   │   └── validators.ts # Zod schemas
│   │   │
│   │   ├── hooks/            # Custom React hooks
│   │   ├── providers/        # React context providers
│   │   ├── styles/           # Design tokens
│   │   └── types/            # TypeScript type definitions
│   │
│   ├── public/               # Static assets
│   ├── package.json
│   ├── tsconfig.json         # TypeScript config (strict mode)
│   ├── tailwind.config.ts    # Tailwind configuration
│   ├── next.config.js        # Next.js configuration
│   └── .env.local            # Environment variables (not in git)
│
├── backend/                   # FastAPI application
│   ├── app/
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── config.py         # Configuration settings
│   │   ├── dependencies.py   # Dependency injection
│   │   │
│   │   ├── api/              # API routes
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py   # Authentication endpoints
│   │   │   │   ├── meals.py  # Meal logging endpoints
│   │   │   │   ├── users.py  # User management
│   │   │   │   └── coach.py  # AI coaching endpoints
│   │   │   └── router.py     # API router aggregation
│   │   │
│   │   ├── models/           # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── meal.py
│   │   │   └── goal.py
│   │   │
│   │   ├── schemas/          # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── meal.py
│   │   │   └── coach.py
│   │   │
│   │   ├── services/         # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── meal_service.py
│   │   │   ├── ai_service.py      # OpenAI integration
│   │   │   └── nutrition_service.py
│   │   │
│   │   ├── db/               # Database related
│   │   │   ├── __init__.py
│   │   │   ├── session.py    # Database session
│   │   │   └── base.py       # Base model
│   │   │
│   │   ├── core/             # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── security.py   # JWT, hashing
│   │   │   └── cache.py      # Redis utilities
│   │   │
│   │   └── utils/            # Utility functions
│   │       └── __init__.py
│   │
│   ├── tests/                # Test suite
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_api/
│   │   └── test_services/
│   │
│   ├── alembic/              # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── requirements.txt      # Python dependencies
│   ├── pyproject.toml        # Python project config
│   ├── .env                  # Environment variables (not in git)
│   └── alembic.ini           # Alembic configuration
│
└── docs/                      # Additional documentation
    ├── api.md                # API documentation
    ├── deployment.md         # Deployment guide
    └── database-schema.md    # Database schema docs
```

---

## 📝 Naming Conventions

### Frontend (TypeScript/React)
- **Files**: `kebab-case.tsx` (e.g., `meal-logger.tsx`)
- **Components**: `PascalCase` (e.g., `MealLogger`)
- **Functions**: `camelCase` (e.g., `handleSubmit`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)
- **Types/Interfaces**: `PascalCase` with descriptive names (e.g., `UserProfile`, `MealData`)
- **Hooks**: `use` prefix (e.g., `useMealLogger`)

### Backend (Python)
- **Files**: `snake_case.py` (e.g., `meal_service.py`)
- **Classes**: `PascalCase` (e.g., `MealService`)
- **Functions**: `snake_case` (e.g., `get_meal_by_id`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- **Models**: `PascalCase` singular (e.g., `User`, `Meal`)
- **API Routes**: `kebab-case` (e.g., `/api/v1/meal-logs`)

### General
- **Environment Variables**: `UPPER_SNAKE_CASE` (e.g., `DATABASE_URL`)
- **Branch Names**: `feature/description` or `fix/description`
- **Commit Messages**: Conventional Commits format

---

## 🚀 Development Commands

### Frontend (Next.js)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Run production build locally
npm run start

# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check

# Run tests
npm run test
```

### Backend (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server (http://localhost:8000)
uvicorn app.main:app --reload --port 8000

# Run with specific host and port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/

# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/

# Type check
mypy app/
```

### Database

```bash
# Start PostgreSQL (if using Docker)
docker run --name weight-coach-db -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15

# Start Redis (if using Docker)
docker run --name weight-coach-redis -p 6379:6379 -d redis:7

# Connect to PostgreSQL
psql -h localhost -U postgres -d weight_coach

# Create database manually (if needed)
createdb weight_coach

# Run migrations (create/update tables)
cd backend
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "description of changes"

# Seed database with sample data
python seed.py

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history

# Check current database version
alembic current
```

#### Database Setup (First Time)

1. **Install PostgreSQL 15+**
   ```bash
   # macOS (with Homebrew)
   brew install postgresql@15
   brew services start postgresql@15

   # Ubuntu/Debian
   sudo apt update
   sudo apt install postgresql-15 postgresql-contrib-15
   sudo systemctl start postgresql

   # Windows - Download installer from postgresql.org
   ```

2. **Create Database**
   ```bash
   # Create database
   createdb weight_coach

   # Or use psql
   psql postgres
   CREATE DATABASE weight_coach;
   \q
   ```

3. **Configure Environment Variables**
   ```bash
   # Create .env file in backend/
   cd backend
   cat > .env << EOF
   DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/weight_coach
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=$(openssl rand -hex 32)
   OPENAI_API_KEY=your-api-key-here
   EOF
   ```

4. **Install Python Dependencies**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Run Migrations**
   ```bash
   # This creates all database tables
   alembic upgrade head
   ```

6. **Seed Sample Data (Optional)**
   ```bash
   # Populate database with test data
   python seed.py
   ```

7. **Verify Setup**
   ```bash
   # Check tables were created
   psql weight_coach
   \dt  # List all tables
   \d users  # Describe users table
   \q

   # Or use a database GUI like pgAdmin, DBeaver, or TablePlus
   ```

#### Database Schema Overview

The database includes 17 tables organized into domains:

**User Domain:**
- `users` - User accounts and authentication
- `user_profiles` - Extended user information
- `user_goals` - Health and fitness goals

**Meal Domain:**
- `meals` - Meal logging
- `meal_items` - Individual food items
- `ai_analyses` - GPT-4 nutrition analysis

**Inventory Domain:**
- `food_categories` - Food categorization
- `inventory_items` - Pantry/fridge tracking

**Recipe Domain:**
- `recipes` - Recipe storage
- `recipe_ingredients` - Recipe ingredients
- `recipe_instructions` - Cooking steps
- `user_recipes` - Saved/favorited recipes

**Planning Domain:**
- `meal_plans` - Weekly/daily meal plans
- `meal_plan_items` - Scheduled meals

**Shopping Domain:**
- `grocery_lists` - Shopping lists
- `grocery_list_items` - List items

**Audit Domain:**
- `activity_logs` - Activity tracking

See `docs/database-design.md` for complete schema documentation.

#### Common Database Tasks

**View all users:**
```bash
psql weight_coach -c "SELECT id, email, is_active FROM users;"
```

**Count records:**
```bash
psql weight_coach -c "
SELECT
  (SELECT COUNT(*) FROM users) as users,
  (SELECT COUNT(*) FROM meals) as meals,
  (SELECT COUNT(*) FROM recipes) as recipes;
"
```

**Reset database (⚠️ Destroys all data):**
```bash
cd backend
alembic downgrade base  # Drop all tables
alembic upgrade head    # Recreate tables
python seed.py          # Restore sample data
```

**Backup database:**
```bash
pg_dump weight_coach > backup.sql

# Restore from backup
psql weight_coach < backup.sql
```

---

## 🎨 Code Style & Standards

### TypeScript (Frontend)

#### General Rules
- **Strict Mode**: Always use TypeScript strict mode
- **Type Safety**: Avoid `any` - use proper types or `unknown`
- **Explicit Returns**: Always specify return types for functions
- **No Unused Vars**: Remove or prefix with `_` if intentionally unused
- **Consistent Imports**: Use absolute imports with `@/` alias

#### Example
```typescript
// Good ✅
interface MealData {
  id: string;
  name: string;
  calories: number;
  createdAt: Date;
}

export async function getMeal(id: string): Promise<MealData> {
  const response = await fetch(`/api/meals/${id}`);
  if (!response.ok) throw new Error('Failed to fetch meal');
  return response.json();
}

// Bad ❌
async function getMeal(id: any) {
  const response = await fetch(`/api/meals/${id}`);
  return response.json();
}
```

#### React Components
- Use functional components with TypeScript
- Prefer named exports for components
- Use React.FC sparingly (prefer explicit prop types)
- Extract complex logic to custom hooks
- Keep components small and focused (< 200 lines)

```typescript
// Good ✅
interface MealCardProps {
  meal: MealData;
  onDelete: (id: string) => void;
}

export function MealCard({ meal, onDelete }: MealCardProps) {
  return (
    <div className="p-4 border rounded-lg">
      <h3>{meal.name}</h3>
      <p>{meal.calories} cal</p>
      <button onClick={() => onDelete(meal.id)}>Delete</button>
    </div>
  );
}
```

### Python (Backend)

#### General Rules
- **Type Hints**: Always use type hints for function parameters and returns
- **Docstrings**: Use Google-style docstrings for functions and classes
- **Error Handling**: Use specific exceptions, avoid bare `except`
- **Async/Await**: Use async for I/O operations (DB, external APIs)
- **Line Length**: Max 100 characters per line

#### Example
```python
# Good ✅
from typing import Optional
from datetime import datetime

async def get_meal_by_id(
    db: AsyncSession,
    meal_id: int,
    user_id: int
) -> Optional[Meal]:
    """
    Retrieve a meal by ID for a specific user.

    Args:
        db: Database session
        meal_id: ID of the meal to retrieve
        user_id: ID of the user who owns the meal

    Returns:
        Meal object if found, None otherwise
    """
    result = await db.execute(
        select(Meal).where(
            Meal.id == meal_id,
            Meal.user_id == user_id
        )
    )
    return result.scalar_one_or_none()

# Bad ❌
def get_meal_by_id(db, meal_id, user_id):
    result = db.execute(select(Meal).where(Meal.id == meal_id))
    return result.scalar_one_or_none()
```

#### FastAPI Routes
- Use dependency injection for DB sessions, auth
- Use Pydantic models for request/response validation
- Include proper HTTP status codes
- Add comprehensive OpenAPI documentation

```python
# Good ✅
@router.post("/meals", response_model=MealResponse, status_code=201)
async def create_meal(
    meal_data: MealCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Meal:
    """
    Create a new meal entry for the authenticated user.
    """
    meal = Meal(**meal_data.dict(), user_id=current_user.id)
    db.add(meal)
    await db.commit()
    await db.refresh(meal)
    return meal
```

### Tailwind CSS

- Use Tailwind utility classes primarily
- Create custom components in `components/ui` for reusable patterns
- Use `cn()` helper for conditional classes
- Prefer Tailwind config for custom colors/spacing

```typescript
// Good ✅
import { cn } from '@/lib/utils';

<div className={cn(
  "p-4 rounded-lg border",
  isActive && "bg-blue-50 border-blue-500",
  disabled && "opacity-50 cursor-not-allowed"
)}>
  Content
</div>
```

---

## 🧪 Testing Approach

### Testing Philosophy

The Weight Coach project follows a **comprehensive testing strategy** to ensure code quality, reliability, and maintainability:

1. **Test-Driven Development (TDD)**: Write tests alongside features
2. **Layered Testing**: Unit, integration, and E2E tests for different layers
3. **High Coverage**: Target 80%+ coverage for backend, 70%+ for frontend
4. **Mock External Services**: Isolate tests from third-party APIs
5. **Fast Feedback**: Tests should run quickly for rapid iteration
6. **CI/CD Ready**: Automated testing on every commit

---

### Backend Testing

#### Test Structure

```
backend/tests/
├── conftest.py                    # Pytest fixtures and configuration
├── pytest.ini                     # Pytest settings and coverage config
├── test_repositories.py           # Repository layer tests (CRUD)
│
├── test_api/                      # Integration tests for API endpoints
│   ├── test_auth.py              # Authentication endpoints
│   ├── test_inventory.py         # Inventory management
│   ├── test_recipes.py           # Recipe CRUD and search
│   ├── test_meal_plans.py        # Meal planning
│   ├── test_grocery_lists.py    # Grocery list management
│   ├── test_coaching.py          # AI coaching endpoints
│   ├── test_voice.py             # Voice assistant WebSocket
│   ├── test_vision.py            # Image recognition
│   └── test_notifications.py    # Notification preferences
│
├── test_services/                 # Service layer unit tests
│   ├── test_openai_service.py   # OpenAI API integration
│   ├── test_voice_command_service.py  # Voice command parsing
│   └── test_image_storage_service.py  # Image upload/storage
│
└── fixtures/                      # Test data and utilities
    ├── audio_samples.py          # Mock audio files
    └── image_samples.py          # Mock images
```

#### Running Backend Tests

**Run all tests:**
```bash
cd backend
pytest
```

**Run with coverage:**
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

**Run specific test file:**
```bash
pytest tests/test_api/test_auth.py
```

**Run specific test class:**
```bash
pytest tests/test_repositories.py::TestUserRepository
```

**Run specific test:**
```bash
pytest tests/test_api/test_auth.py::test_register_user
```

**Run with markers:**
```bash
# Only unit tests
pytest -m unit

# Only integration tests
pytest -m integration

# Only database tests
pytest -m database

# Exclude slow tests
pytest -m "not slow"
```

**Run in parallel (faster):**
```bash
pytest -n auto  # Uses all CPU cores
```

**View coverage report:**
```bash
# Generate HTML report
pytest --cov=app --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

#### Test Configuration (pytest.ini)

```ini
[pytest]
# Test discovery patterns
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Test paths
testpaths = tests

# Output and coverage options
addopts =
    -v                          # Verbose output
    --strict-markers            # Enforce marker registration
    --tb=short                  # Short traceback format
    --cov=app                   # Coverage for app/ directory
    --cov-report=term-missing   # Show missing lines in terminal
    --cov-report=html           # Generate HTML coverage report
    --cov-report=xml            # Generate XML for CI tools
    --cov-branch                # Branch coverage
    --cov-fail-under=80         # Fail if coverage < 80%

# Test markers
markers =
    unit: Unit tests for individual components
    integration: Integration tests for API endpoints
    slow: Tests that take longer to run
    database: Tests that require database access
    external: Tests that mock external services

# Async support
asyncio_mode = auto

# Warnings
filterwarnings =
    error
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

#### Test Fixtures (conftest.py)

The `conftest.py` file provides reusable test fixtures:

**Database Fixtures:**
```python
@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Provides clean database session for each test"""
    # Creates test database, runs migrations, yields session, then cleans up

@pytest.fixture
async def test_user(db: AsyncSession) -> User:
    """Creates a test user"""

@pytest.fixture
async def verified_user(db: AsyncSession) -> User:
    """Creates a verified test user"""

@pytest.fixture
async def admin_user(db: AsyncSession) -> User:
    """Creates an admin test user"""
```

**HTTP Client Fixtures:**
```python
@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provides HTTP test client for API testing"""

@pytest.fixture
async def auth_headers(test_user: User) -> dict:
    """Provides authentication headers with valid JWT token"""
```

**Mock Fixtures:**
```python
@pytest.fixture
def mock_openai_chat_response():
    """Mocks OpenAI chat completion response"""

@pytest.fixture
def mock_openai_vision_response():
    """Mocks OpenAI vision analysis response"""

@pytest.fixture
def mock_whisper_transcription():
    """Mocks Whisper audio transcription"""
```

#### Writing Tests

**Repository Tests Example:**
```python
# tests/test_repositories.py
import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.inventory import InventoryItem, FoodCategory
from app.repositories.inventory_repository import inventory_repository

class TestInventoryRepository:
    """Test inventory repository operations"""

    @pytest.mark.asyncio
    async def test_create_inventory_item(self, db: AsyncSession, test_user):
        """Test creating an inventory item"""
        item_data = {
            "user_id": test_user.id,
            "name": "Chicken Breast",
            "quantity": 500.0,
            "unit": "g",
            "category": FoodCategory.MEAT,
            "location": "fridge",
        }

        item = await inventory_repository.create(db, item_data)
        await db.commit()
        await db.refresh(item)

        assert item.id is not None
        assert item.name == "Chicken Breast"
        assert item.quantity == 500.0
        assert item.category == FoodCategory.MEAT

    @pytest.mark.asyncio
    async def test_filter_expiring_soon(self, db: AsyncSession, test_user):
        """Test filtering items expiring soon"""
        # Create item expiring in 2 days
        item_data = {
            "user_id": test_user.id,
            "name": "Milk",
            "quantity": 1000.0,
            "unit": "ml",
            "category": FoodCategory.DAIRY,
            "expiry_date": datetime.utcnow() + timedelta(days=2),
        }
        await inventory_repository.create(db, item_data)
        await db.commit()

        # Get items expiring within 3 days
        expiring_items = await inventory_repository.get_expiring_soon(
            db, test_user.id, days=3
        )

        assert len(expiring_items) >= 1
        assert all(
            item.expiry_date <= datetime.utcnow() + timedelta(days=3)
            for item in expiring_items
            if item.expiry_date
        )
```

**API Integration Tests Example:**
```python
# tests/test_api/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "New User"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data
    assert "password" not in data  # Never return password

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword"  # Default test user password
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers, test_user):
    """Test retrieving current authenticated user"""
    response = await client.get(
        "/api/v1/auth/me",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
```

**Service Tests with Mocking:**
```python
# tests/test_services/test_openai_service.py
import pytest
from unittest.mock import AsyncMock, patch
from app.services.openai_service import openai_service

@pytest.mark.asyncio
async def test_analyze_meal_with_ai(mock_openai_chat_response):
    """Test meal analysis with mocked OpenAI response"""
    with patch('openai.ChatCompletion.acreate',
               new_callable=AsyncMock,
               return_value=mock_openai_chat_response):

        result = await openai_service.analyze_meal(
            meal_description="Grilled chicken with rice and vegetables"
        )

        assert result is not None
        assert "calories" in result
        assert "protein_g" in result
        assert result["calories"] > 0

@pytest.mark.asyncio
async def test_parse_voice_command():
    """Test voice command parsing"""
    result = await openai_service.parse_voice_command(
        transcript="Set a timer for 10 minutes",
        context={"current_step": 1, "recipe_name": "Pasta"}
    )

    assert result["action"] == "set_timer"
    assert result["parameters"]["duration"] == 600  # 10 minutes in seconds
```

#### Mocking External Services

**OpenAI API Mocking:**

The conftest.py provides mock fixtures for all OpenAI services:

```python
# In your tests
@pytest.mark.asyncio
async def test_with_mocked_openai(mock_openai_chat_response):
    """OpenAI calls are automatically mocked"""
    with patch('openai.ChatCompletion.acreate',
               return_value=mock_openai_chat_response):
        # Test code that calls OpenAI
        result = await some_function_using_openai()
        assert result is not None
```

**Redis Mocking:**

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mocked_redis():
    """Mock Redis cache operations"""
    with patch('redis.asyncio.Redis') as mock_redis:
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock(return_value=True)

        # Test code that uses Redis
        await cache.set("key", "value")
        mock_redis.set.assert_called_once()
```

#### Coverage Requirements

- **Minimum Coverage**: 80% for backend code
- **Critical Paths**: 90%+ for auth, payments, data integrity
- **Generated Code**: Excluded (migrations, auto-generated models)
- **Coverage Reports**: Generated on every test run

**View coverage gaps:**
```bash
pytest --cov=app --cov-report=term-missing

# Shows which lines are not covered:
# app/services/meal_service.py    85%   45-47, 62
```

**Coverage exclusions (in pytest.ini):**
```ini
[coverage:run]
omit =
    */tests/*
    */migrations/*
    */__pycache__/*
    */venv/*
    */env/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
```

---

### Frontend Testing

#### Test Structure

```
frontend/
├── __tests__/                     # Global test utilities
│   └── setup.ts                  # Jest setup
│
└── components/
    ├── ui/
    │   ├── button.tsx
    │   └── button.test.tsx       # Component tests
    │
    └── features/
        ├── meals/
        │   ├── meal-logger.tsx
        │   └── meal-logger.test.tsx
        │
        └── dashboard/
            ├── nutrition-chart.tsx
            └── nutrition-chart.test.tsx
```

#### Running Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode (for development)
npm run test:watch

# Run specific test file
npm test -- meal-logger.test.tsx

# Update snapshots
npm test -- -u
```

#### Frontend Test Example

```typescript
// components/ui/button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './button';

describe('Button Component', () => {
  it('renders button text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('disables button when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);
    const button = screen.getByRole('button');

    expect(button).toBeDisabled();
  });
});

// components/features/meals/meal-logger.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MealLogger } from './meal-logger';

describe('MealLogger', () => {
  it('submits meal data', async () => {
    const onSubmit = jest.fn();
    render(<MealLogger onSubmit={onSubmit} />);

    await userEvent.type(
      screen.getByLabelText('Meal description'),
      'Chicken salad'
    );
    await userEvent.click(screen.getByRole('button', { name: /log meal/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          description: 'Chicken salad'
        })
      );
    });
  });
});
```

---

### Test Organization Best Practices

1. **Descriptive Test Names**: Use clear, intention-revealing names
   ```python
   # Good ✅
   async def test_user_cannot_delete_another_users_meal()

   # Bad ❌
   async def test_delete_meal()
   ```

2. **AAA Pattern**: Arrange, Act, Assert
   ```python
   async def test_create_inventory_item(db, test_user):
       # Arrange
       item_data = {"name": "Milk", "quantity": 1000}

       # Act
       item = await inventory_repository.create(db, item_data)

       # Assert
       assert item.name == "Milk"
   ```

3. **One Assertion Per Test** (when practical)
   ```python
   # Test one behavior per test function
   async def test_expired_items_are_filtered_out()
   async def test_items_are_sorted_by_expiry_date()
   ```

4. **Mock External Services**: Never call real APIs in tests
   ```python
   @patch('openai.ChatCompletion.acreate')
   async def test_ai_analysis(mock_openai):
       mock_openai.return_value = mock_response
       # Test code
   ```

5. **Clean Test Data**: Each test should be isolated
   ```python
   # Use fixtures that create fresh data per test
   @pytest.fixture
   async def test_user(db):
       user = create_user()
       yield user
       # Cleanup handled by transaction rollback
   ```

---

### CI/CD Integration

#### GitHub Actions Workflow

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests with coverage
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run tests
        run: |
          cd frontend
          npm run test:coverage
```

#### Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: bash -c 'cd backend && pytest tests/ -v'
        language: system
        pass_filenames: false
        always_run: true
```

---

### Test Runner Scripts

#### Backend Test Runner

Create `backend/run_tests.sh`:

```bash
#!/bin/bash
# Backend test runner script

set -e  # Exit on error

echo "🧪 Running Weight Coach Backend Tests..."
echo "========================================"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run tests with coverage
pytest tests/ \
    --cov=app \
    --cov-report=html \
    --cov-report=xml \
    --cov-report=term-missing \
    --cov-fail-under=80 \
    -v \
    "$@"  # Pass any additional arguments

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo "📊 Coverage report generated: htmlcov/index.html"
else
    echo ""
    echo "❌ Tests failed!"
    exit 1
fi
```

Make executable:
```bash
chmod +x backend/run_tests.sh
```

Usage:
```bash
# Run all tests
./run_tests.sh

# Run with additional pytest args
./run_tests.sh -k test_auth
./run_tests.sh -m "not slow"
```

---

### Troubleshooting Tests

**Issue: Database connection errors**
```bash
# Ensure test database exists
createdb test_weight_coach

# Check DATABASE_URL in .env.test
cat backend/.env.test
```

**Issue: Async tests not running**
```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Ensure asyncio_mode = auto in pytest.ini
```

**Issue: Import errors**
```bash
# Add backend directory to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"

# Or install in development mode
cd backend
pip install -e .
```

**Issue: Tests are slow**
```bash
# Run in parallel
pytest -n auto

# Skip slow tests
pytest -m "not slow"

# Increase test database pool size in conftest.py
```

---

### Testing Checklist

When adding new features, ensure:

- [ ] Repository tests for new models
- [ ] Service tests for business logic
- [ ] API integration tests for new endpoints
- [ ] Mock external service calls
- [ ] Test error cases and edge cases
- [ ] Test authentication/authorization
- [ ] Achieve 80%+ coverage for new code
- [ ] All tests pass before committing
- [ ] Update this documentation if needed

---

## 🏗️ Backend Development Conventions

### Architecture Overview

The backend follows a **layered architecture** pattern:

```
API Routes (Presentation Layer)
       ↓
Services (Business Logic Layer)
       ↓
Repositories (Data Access Layer)
       ↓
Models (Database Layer)
```

### Adding a New Feature

Follow these steps when adding a new feature to the backend:

#### 1. Create Database Model (if needed)

```python
# app/models/my_model.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin

class MyModel(Base, TimestampMixin):
    __tablename__ = "my_table"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="my_models")
```

**Then create migration:**
```bash
cd backend
alembic revision --autogenerate -m "add my_table"
alembic upgrade head
```

#### 2. Create Pydantic Schemas

```python
# app/schemas/my_schema.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MySchemaBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

class MySchemaCreate(MySchemaBase):
    """Schema for creating new record"""
    pass

class MySchemaUpdate(BaseModel):
    """Schema for updating record (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)

class MySchemaResponse(MySchemaBase):
    """Schema for API responses"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)
```

#### 3. Create Repository

```python
# app/repositories/my_repository.py
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.my_model import MyModel

class MyRepository(BaseRepository[MyModel]):
    """Repository for MyModel data access"""

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[MyModel]:
        """Get all records for a specific user"""
        result = await db.execute(
            select(MyModel)
            .where(MyModel.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_name(
        self,
        db: AsyncSession,
        name: str,
        user_id: int
    ) -> Optional[MyModel]:
        """Find record by name for specific user"""
        result = await db.execute(
            select(MyModel)
            .where(
                MyModel.name == name,
                MyModel.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

# Create singleton instance
my_repository = MyRepository(MyModel)
```

#### 4. Create Service

```python
# app/services/my_service.py
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.my_repository import my_repository
from app.schemas.my_schema import MySchemaCreate, MySchemaUpdate
from app.models.my_model import MyModel
from app.core.exceptions import NotFoundException, ConflictException
from app.core.logging import get_logger

logger = get_logger(__name__)

class MyService:
    """Business logic for MyModel"""

    async def create_my_record(
        self,
        db: AsyncSession,
        data: MySchemaCreate,
        user_id: int
    ) -> MyModel:
        """Create new record with validation"""
        # Check for duplicates
        existing = await my_repository.get_by_name(db, data.name, user_id)
        if existing:
            raise ConflictException(
                f"Record with name '{data.name}' already exists",
                error_code="DUPLICATE_NAME"
            )

        # Create record
        record_data = data.dict()
        record_data["user_id"] = user_id

        logger.info(f"Creating new record for user {user_id}")
        record = await my_repository.create(db, record_data)

        return record

    async def get_user_records(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[MyModel]:
        """Get all records for user"""
        return await my_repository.get_by_user(db, user_id, skip, limit)

    async def update_record(
        self,
        db: AsyncSession,
        record_id: int,
        data: MySchemaUpdate,
        user_id: int
    ) -> MyModel:
        """Update existing record"""
        # Get and verify ownership
        record = await my_repository.get(db, record_id)
        if not record:
            raise NotFoundException("Record not found", error_code="RECORD_NOT_FOUND")

        if record.user_id != user_id:
            raise NotFoundException("Record not found")  # Don't reveal it exists

        # Update
        logger.info(f"Updating record {record_id}")
        updated = await my_repository.update(db, record, data.dict(exclude_unset=True))

        return updated

    async def delete_record(
        self,
        db: AsyncSession,
        record_id: int,
        user_id: int
    ) -> bool:
        """Soft delete record"""
        record = await my_repository.get(db, record_id)
        if not record or record.user_id != user_id:
            raise NotFoundException("Record not found")

        logger.info(f"Deleting record {record_id}")
        await my_repository.soft_delete(db, record_id)

        return True

# Create singleton instance
my_service = MyService()
```

#### 5. Create API Routes

```python
# app/api/v1/my_routes.py
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user, PaginationParams
from app.services.my_service import my_service
from app.schemas.my_schema import (
    MySchemaCreate,
    MySchemaUpdate,
    MySchemaResponse
)
from app.models.user import User

router = APIRouter(
    prefix="/my-resource",
    tags=["My Resource"]
)

@router.post(
    "/",
    response_model=MySchemaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new record",
    description="Create a new record for the authenticated user"
)
async def create_record(
    data: MySchemaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MySchemaResponse:
    """Create a new record"""
    record = await my_service.create_my_record(db, data, current_user.id)
    return record

@router.get(
    "/",
    response_model=List[MySchemaResponse],
    summary="Get all records",
    description="Retrieve all records for the authenticated user"
)
async def get_records(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[MySchemaResponse]:
    """Get all user's records with pagination"""
    records = await my_service.get_user_records(
        db,
        current_user.id,
        skip=pagination.skip,
        limit=pagination.limit
    )
    return records

@router.get(
    "/{record_id}",
    response_model=MySchemaResponse,
    summary="Get record by ID"
)
async def get_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MySchemaResponse:
    """Get specific record by ID"""
    # Service will validate ownership
    record = await my_service.get_record_by_id(db, record_id, current_user.id)
    return record

@router.patch(
    "/{record_id}",
    response_model=MySchemaResponse,
    summary="Update record"
)
async def update_record(
    record_id: int,
    data: MySchemaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MySchemaResponse:
    """Update existing record"""
    record = await my_service.update_record(db, record_id, data, current_user.id)
    return record

@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete record"
)
async def delete_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """Soft delete a record"""
    await my_service.delete_record(db, record_id, current_user.id)
```

#### 6. Register Router

```python
# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1 import auth, my_routes

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(my_routes.router)  # Add your new router
```

#### 7. Write Tests

```python
# tests/test_api/test_my_routes.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_record(client: AsyncClient, auth_headers: dict):
    """Test creating a new record"""
    response = await client.post(
        "/api/v1/my-resource/",
        json={"name": "Test Record"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Record"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_records(client: AsyncClient, auth_headers: dict):
    """Test retrieving user records"""
    response = await client.get(
        "/api/v1/my-resource/",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Best Practices

#### Error Handling

Always use custom exceptions from `app.core.exceptions`:

```python
from app.core.exceptions import (
    NotFoundException,
    UnauthorizedException,
    ConflictException,
    ValidationException
)

# In services
if not user:
    raise NotFoundException(
        "User not found",
        error_code="USER_NOT_FOUND"
    )

if existing_email:
    raise ConflictException(
        "Email already registered",
        error_code="EMAIL_CONFLICT",
        details={"email": email}
    )
```

#### Database Sessions

Always use dependency injection for database sessions:

```python
from app.api.deps import get_db

@router.get("/items")
async def get_items(db: AsyncSession = Depends(get_db)):
    # db session is automatically managed
    # No need to manually close or commit in routes
    pass
```

#### Logging

Use structured logging throughout:

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

logger.info("Processing request", extra={"user_id": user.id})
logger.error("Failed to process", extra={"error": str(e)})
```

#### Authentication

Protect routes with authentication:

```python
from app.api.deps import get_current_user

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user)
):
    # Route automatically requires valid JWT token
    # current_user contains authenticated user
    pass
```

### Running the Backend Server

#### Development Mode

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run with auto-reload
uvicorn app.main:app --reload --port 8000

# Run with custom host and port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run with log level
uvicorn app.main:app --reload --log-level debug
```

#### Access API Documentation

Once running, access interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

#### Production Mode

```bash
# Without reload (better performance)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# With Gunicorn (production recommended)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Common Backend Tasks

#### Check API Health

```bash
curl http://localhost:8000/health
```

#### Test Authentication Flow

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Use token (replace <TOKEN> with actual token)
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <TOKEN>"
```

#### View Logs

```bash
# Application logs (if file logging enabled)
tail -f backend/logs/app.log

# Uvicorn server logs (console)
# Automatically displayed when running with --reload
```

### Troubleshooting

**Issue: Import errors when starting server**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Issue: Database connection errors**
```bash
# Check PostgreSQL is running
pg_isready

# Verify DATABASE_URL in .env
cat .env | grep DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

**Issue: Migration errors**
```bash
# Check current migration state
alembic current

# View migration history
alembic history

# Rollback and retry
alembic downgrade -1
alembic upgrade head
```

---

## 🔐 Environment Variables

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/weight_coach
DATABASE_POOL_SIZE=5

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=1000

# CORS
CORS_ORIGINS=["http://localhost:3000", "https://yourapp.vercel.app"]

# Environment
ENVIRONMENT=development
DEBUG=True
```

**Security**: Never commit `.env` files. Use `.env.example` for templates.

---

## 🔄 Git Workflow

### Branch Strategy
- **Main Branch**: `main` - production-ready code
- **Feature Branches**: `feature/feature-name`
- **Bug Fixes**: `fix/bug-description`
- **Hotfixes**: `hotfix/issue-description`

### Commit Message Format
Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples**:
```bash
feat(frontend): add meal image upload component
fix(backend): resolve nutrition calculation error
docs: update API documentation for meals endpoint
refactor(backend): simplify AI service error handling
```

### Workflow
```bash
# 1. Create feature branch
git checkout -b feature/meal-voice-input

# 2. Make changes and commit frequently
git add .
git commit -m "feat(frontend): add voice recording component"

# 3. Push to remote
git push -u origin feature/meal-voice-input

# 4. Create Pull Request on GitHub
# 5. After review and approval, merge to main
# 6. Delete feature branch
```

---

## 🚢 Deployment

### Frontend (Vercel)
1. Connect GitHub repository to Vercel
2. Configure build settings:
   - Framework: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`
3. Set environment variables in Vercel dashboard
4. Deploy automatically on push to `main`

### Backend (Railway)
1. Create new project in Railway
2. Add PostgreSQL and Redis services
3. Deploy from GitHub:
   - Root Directory: `backend`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set environment variables
5. Run migrations: `alembic upgrade head`

### Database Migrations
```bash
# Before deploying backend changes with DB schema updates
alembic revision --autogenerate -m "add meal images table"
alembic upgrade head

# On Railway, set up to auto-run migrations on deploy
```

---

## 📚 Key Dependencies

### Frontend
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "typescript": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "axios": "^1.6.0",
    "react-hook-form": "^7.48.0",
    "zod": "^3.22.0",
    "@radix-ui/react-*": "latest",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0"
  }
}
```

### Backend
```python
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis==5.0.1
openai==1.3.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
black==23.11.0
isort==5.12.0
mypy==1.7.0
```

---

## 🎯 Development Priorities (Hackathon)

### MVP Features (Day 1)
1. ✅ User authentication (signup/login)
2. ✅ Basic meal logging (text input)
3. ✅ Simple calorie tracking
4. ✅ Dashboard with daily summary

### Enhanced Features (Day 2)
5. ✅ AI nutrition analysis with GPT-4
6. ✅ Voice input with Whisper
7. ✅ Image recognition with Vision
8. ✅ Progress charts and visualization

### Polish (Day 3)
9. ✅ Responsive design improvements
10. ✅ Error handling and loading states
11. ✅ Performance optimization
12. ✅ Demo preparation and deployment

---

## 🐛 Common Issues & Solutions

### Issue: CORS errors when calling backend
**Solution**: Ensure `CORS_ORIGINS` includes frontend URL in backend `.env`

### Issue: Database connection failed
**Solution**: Check `DATABASE_URL` format and PostgreSQL is running

### Issue: OpenAI API rate limits
**Solution**: Implement caching with Redis, add retry logic with exponential backoff

### Issue: Slow image processing
**Solution**: Compress images on frontend before upload, use background tasks in FastAPI

---

## 📖 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)

---

## 🤝 Contributing Guidelines

Since this is a hackathon project, move fast but maintain code quality:

1. **Test before committing**: Ensure code runs without errors
2. **Write clear commits**: Use conventional commit format
3. **Document as you go**: Update this file when architecture changes
4. **Ask before major changes**: Discuss significant architectural decisions
5. **Keep it simple**: Prioritize working features over perfect code

---

## 📝 Notes

- This is a **hackathon project** - prioritize shipping over perfection
- Focus on **core user value**: meal logging and AI insights
- **Cache aggressively**: OpenAI API calls are expensive
- **Design for demos**: Make it visually impressive
- **Mobile-first**: Most users will test on phones

---

**Remember**: This CLAUDE.md file is the single source of truth for the project. Keep it updated as the project evolves!
