"""
Activity log Pydantic schemas for request/response validation.
"""

from typing import Any, Dict, Optional

from pydantic import Field

from app.schemas.base import BaseSchema, TimestampSchema


class ActivityLogBase(BaseSchema):
    """Base activity log schema."""

    activity_type: str = Field(..., min_length=1, max_length=50)
    entity_type: str = Field(..., min_length=1, max_length=50)
    entity_id: Optional[int] = None
    changes: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = Field(None, max_length=45)


class ActivityLogCreate(ActivityLogBase):
    """Schema for creating activity log."""

    user_id: Optional[int] = None


class ActivityLogResponse(ActivityLogBase, TimestampSchema):
    """Schema for activity log responses."""

    id: int
    user_id: Optional[int] = None
