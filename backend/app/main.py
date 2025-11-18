"""
Weight Coach - FastAPI Application Entry Point.

This module initializes and configures the FastAPI application with:
- CORS middleware for frontend integration
- Exception handlers for error responses
- Logging configuration
- Database connection management
- API router registration
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.db.database import close_db, init_db
from app.middleware import RequestLoggerMiddleware, register_exception_handlers

# Set up logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Startup: Initialize database connections, cache, etc.
    - Shutdown: Close connections gracefully
    """
    # Startup
    logger.info("🚀 Starting Weight Coach API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Initialize database (only if needed for testing)
    if settings.ENVIRONMENT == "development" and settings.DEBUG:
        logger.info("Initializing database tables (development mode)...")
        # await init_db()  # Uncomment if you want to auto-create tables in dev

    logger.info("✅ Application startup complete")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Weight Coach API...")

    # Close database connections
    await close_db()

    logger.info("✅ Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Nutrition Coach API",
    docs_url="/docs" if settings.DEBUG else None,  # Disable docs in production
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-Total-Count"],
)

# Add request logging middleware
app.add_middleware(RequestLoggerMiddleware)

# Register exception handlers
register_exception_handlers(app)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns:
        Status information about the API
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict:
    """
    Root endpoint with API information.

    Returns:
        API welcome message and documentation links
    """
    return {
        "message": "Welcome to Weight Coach API",
        "version": settings.VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
        "health": "/health",
    }


# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Development server startup message
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting development server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
