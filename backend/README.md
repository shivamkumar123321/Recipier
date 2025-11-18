# Weight Coach - Backend API

FastAPI-based backend for the Weight Coach nutrition coaching application.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- OpenAI API key

### Installation

1. **Create virtual environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run database migrations:**
```bash
alembic upgrade head
```

5. **Seed the database (optional):**
```bash
python seed.py
```

6. **Start the server:**
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🏗️ Architecture

### Layered Architecture

```
┌─────────────────────────────────────┐
│      API Routes (Presentation)      │  ← FastAPI endpoints
├─────────────────────────────────────┤
│      Services (Business Logic)      │  ← Core business logic
├─────────────────────────────────────┤
│    Repositories (Data Access)       │  ← Database operations
├─────────────────────────────────────┤
│      Models (Database Layer)        │  ← SQLAlchemy models
└─────────────────────────────────────┘
```

### Directory Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration settings
│   ├── dependencies.py         # Dependency injection
│   │
│   ├── api/                    # API routes
│   │   └── v1/                 # API version 1
│   │       ├── router.py       # Main router
│   │       ├── auth.py         # Auth endpoints
│   │       ├── meals.py        # Meal endpoints
│   │       └── ...
│   │
│   ├── core/                   # Core functionality
│   │   ├── config.py           # Settings
│   │   ├── security.py         # JWT, password hashing
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── logging.py          # Logging config
│   │
│   ├── db/                     # Database
│   │   ├── base.py             # Base model
│   │   └── database.py         # Session management
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── meal.py
│   │   └── ...
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── meal.py
│   │   └── ...
│   │
│   ├── repositories/           # Data access layer
│   │   ├── base.py             # Base repository
│   │   ├── user_repository.py
│   │   └── ...
│   │
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   ├── meal_service.py
│   │   └── ...
│   │
│   ├── middleware/             # Custom middleware
│   │   ├── error_handler.py
│   │   └── request_logger.py
│   │
│   └── utils/                  # Utilities
│       └── datetime.py
│
├── tests/                      # Test suite
├── alembic/                    # Database migrations
├── requirements.txt            # Dependencies
├── .env.example                # Environment template
└── seed.py                     # Database seeding
```

## 🔧 Development Workflow

### Adding a New Feature

1. **Create database models** (if needed):
```python
# app/models/my_model.py
from app.db.base import Base, TimestampMixin

class MyModel(Base, TimestampMixin):
    __tablename__ = "my_table"
    # ... fields
```

2. **Create Pydantic schemas**:
```python
# app/schemas/my_schema.py
from pydantic import BaseModel

class MySchema(BaseModel):
    field1: str
    field2: int
```

3. **Create repository**:
```python
# app/repositories/my_repository.py
from app.repositories.base import BaseRepository
from app.models.my_model import MyModel

class MyRepository(BaseRepository[MyModel]):
    async def custom_query(self, db, param):
        # Custom database operations
        pass

my_repository = MyRepository(MyModel)
```

4. **Create service**:
```python
# app/services/my_service.py
from app.repositories.my_repository import my_repository

class MyService:
    async def do_something(self, db, data):
        # Business logic here
        return await my_repository.create(db, data)

my_service = MyService()
```

5. **Create API endpoints**:
```python
# app/api/v1/my_routes.py
from fastapi import APIRouter, Depends
from app.api.deps import get_db
from app.services.my_service import my_service

router = APIRouter(prefix="/my-resource", tags=["My Resource"])

@router.post("/", status_code=201)
async def create_resource(data: MySchema, db = Depends(get_db)):
    return await my_service.do_something(db, data)
```

6. **Register router**:
```python
# app/api/v1/router.py
from app.api.v1.my_routes import router as my_router

api_router.include_router(my_router)
```

7. **Create migration**:
```bash
alembic revision --autogenerate -m "add my_table"
alembic upgrade head
```

8. **Write tests**:
```python
# tests/test_api/test_my_routes.py
import pytest

@pytest.mark.asyncio
async def test_create_resource(client, auth_headers):
    response = await client.post("/api/v1/my-resource/",
                                  json={"field1": "value"},
                                  headers=auth_headers)
    assert response.status_code == 201
```

## 🧪 Testing

### Run all tests:
```bash
pytest
```

### Run with coverage:
```bash
pytest --cov=app tests/
```

### Run specific test file:
```bash
pytest tests/test_api/test_auth.py
```

### Run with verbose output:
```bash
pytest -v
```

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Register**: `POST /api/v1/auth/register`
2. **Login**: `POST /api/v1/auth/login` (returns access + refresh tokens)
3. **Use access token** in `Authorization: Bearer <token>` header
4. **Refresh**: `POST /api/v1/auth/refresh` (get new access token)

### Example:
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123","full_name":"John Doe"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Use token
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## 📦 Database Management

### Create new migration:
```bash
alembic revision --autogenerate -m "description"
```

### Apply migrations:
```bash
alembic upgrade head
```

### Rollback migration:
```bash
alembic downgrade -1
```

### View migration history:
```bash
alembic history
```

### Seed database with sample data:
```bash
python seed.py
```

## 🔍 Logging

Logs are configured with structured logging:

- **Console output**: Colored logs for development
- **File output**: `logs/app.log` for production
- **Log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Log locations:
- Application logs: `logs/app.log`
- Error logs: Captured in main log with ERROR level

### Example usage in code:
```python
from app.core.logging import get_logger

logger = get_logger(__name__)

logger.info("Processing request")
logger.error("Failed to process", extra={"user_id": user.id})
```

## ⚡ Performance

### Caching with Redis

Redis is used for:
- Session storage
- API response caching
- Rate limiting

### Database Optimization

- **Connection pooling**: Configured in `DATABASE_POOL_SIZE`
- **Async operations**: All DB operations use async/await
- **Eager loading**: Use `selectinload()` to avoid N+1 queries
- **Indexes**: Added on frequently queried columns

## 🚨 Error Handling

The API uses custom exception hierarchy:

```python
from app.core.exceptions import NotFoundException, UnauthorizedException

# In your code:
if not user:
    raise NotFoundException("User not found", error_code="USER_NOT_FOUND")
```

**Standard error response:**
```json
{
  "detail": "User not found",
  "error_code": "USER_NOT_FOUND",
  "status_code": 404,
  "timestamp": "2025-11-18T10:30:00Z"
}
```

## 🔒 Security Best Practices

- **Password hashing**: bcrypt via passlib
- **JWT tokens**: Signed with HS256 algorithm
- **CORS**: Configured for frontend origins only
- **Input validation**: Pydantic schemas
- **SQL injection**: Protected by SQLAlchemy ORM
- **Rate limiting**: Implemented with slowapi

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-18T10:30:00Z"
}
```

### Database Health

```bash
curl http://localhost:8000/health/db
```

## 🐛 Common Issues

### Issue: Database connection failed
**Solution**:
- Check PostgreSQL is running: `pg_isready`
- Verify `DATABASE_URL` in `.env`
- Ensure database exists: `createdb weight_coach`

### Issue: Import errors
**Solution**:
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

### Issue: Migration conflicts
**Solution**:
```bash
alembic downgrade -1
alembic revision --autogenerate -m "fix migration"
alembic upgrade head
```

### Issue: Redis connection failed
**Solution**:
- Check Redis is running: `redis-cli ping`
- Verify `REDIS_URL` in `.env`

## 🌐 Environment Variables

See `.env.example` for all available configuration options.

**Required variables:**
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key (use `openssl rand -hex 32`)
- `OPENAI_API_KEY`: OpenAI API key

**Optional variables:**
- `REDIS_URL`: Redis connection (default: localhost)
- `CORS_ORIGINS`: Allowed origins (default: localhost:3000)
- `DEBUG`: Debug mode (default: False)

## 📝 Code Style

### Python Style Guide

- **Formatting**: black (line length: 100)
- **Import sorting**: isort
- **Linting**: flake8
- **Type checking**: mypy

### Format code:
```bash
black app/
isort app/
```

### Lint code:
```bash
flake8 app/
mypy app/
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production `DATABASE_URL`
- [ ] Set up SSL/TLS
- [ ] Configure CORS for production domain
- [ ] Set up monitoring and logging
- [ ] Run migrations on production DB
- [ ] Set up automatic backups

### Railway Deployment

1. Create new project in Railway
2. Add PostgreSQL and Redis services
3. Set environment variables
4. Deploy from GitHub
5. Run migrations: `alembic upgrade head`

**Start command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 📞 Support

For issues and questions:
- Check `docs/` directory for detailed documentation
- Review API documentation at `/docs`
- Check CLAUDE.md for project conventions

## 📄 License

See LICENSE file for details.
