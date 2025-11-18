"""
Custom exception classes for the Weight Coach API.

Provides a hierarchy of exceptions for different error scenarios
with proper HTTP status codes and error messages.
"""

from typing import Any, Dict, Optional


class WeightCoachException(Exception):
    """Base exception for all Weight Coach API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(WeightCoachException):
    """Resource not found (404)."""

    def __init__(
        self,
        resource: str,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with id {resource_id} not found"

        super().__init__(
            message=message,
            status_code=404,
            error_code=f"{resource.upper()}_NOT_FOUND",
            details=details,
        )


class UnauthorizedException(WeightCoachException):
    """Unauthorized access (401)."""

    def __init__(
        self,
        message: str = "Unauthorized access",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED",
            details=details,
        )


class ForbiddenException(WeightCoachException):
    """Forbidden access (403)."""

    def __init__(
        self,
        message: str = "Access forbidden",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
            details=details,
        )


class BadRequestException(WeightCoachException):
    """Bad request (400)."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=400,
            error_code="BAD_REQUEST",
            details=details,
        )


class ValidationException(WeightCoachException):
    """Validation error (422)."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if field:
            error_details["field"] = field

        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=error_details,
        )


class ConflictException(WeightCoachException):
    """Resource conflict (409)."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details=details,
        )


class RateLimitException(WeightCoachException):
    """Rate limit exceeded (429)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please try again later.",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
        )


class ServiceUnavailableException(WeightCoachException):
    """Service unavailable (503)."""

    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=503,
            error_code="SERVICE_UNAVAILABLE",
            details=details,
        )


class ExternalAPIException(WeightCoachException):
    """External API error (502)."""

    def __init__(
        self,
        service: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_message = message or f"Error communicating with {service}"
        error_details = details or {}
        error_details["service"] = service

        super().__init__(
            message=error_message,
            status_code=502,
            error_code="EXTERNAL_API_ERROR",
            details=error_details,
        )
