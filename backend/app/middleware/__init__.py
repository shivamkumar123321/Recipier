"""
Middleware package for Weight Coach API.
"""

from app.middleware.error_handler import register_exception_handlers
from app.middleware.request_logger import RequestLoggerMiddleware

__all__ = [
    "register_exception_handlers",
    "RequestLoggerMiddleware",
]
