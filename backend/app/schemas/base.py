"""
Base Pydantic schemas with common patterns.

Provides base classes for request/response schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Base schema with common configuration.

    Enables ORM mode for SQLAlchemy model conversion.
    """

    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(BaseSchema):
    """
    Schema mixin for timestamp fields.

    Includes created_at and updated_at timestamps.
    """

    created_at: datetime
    updated_at: datetime


class SoftDeleteSchema(BaseSchema):
    """
    Schema mixin for soft delete fields.

    Includes deleted_at timestamp.
    """

    deleted_at: Optional[datetime] = None
