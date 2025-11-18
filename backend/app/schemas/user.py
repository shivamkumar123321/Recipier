"""
User-related Pydantic schemas for request/response validation.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import EmailStr, Field, field_validator

from app.schemas.base import BaseSchema, SoftDeleteSchema, TimestampSchema


# User Schemas
class UserBase(BaseSchema):
    """Base user schema with common fields."""

    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseSchema):
    """Schema for updating user information."""

    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(UserBase, TimestampSchema, SoftDeleteSchema):
    """Schema for user responses (excludes password)."""

    id: int
    is_active: bool
    is_verified: bool


class UserLogin(BaseSchema):
    """Schema for user login."""

    email: EmailStr
    password: str


class TokenResponse(BaseSchema):
    """Schema for JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseSchema):
    """Schema for token refresh request."""

    refresh_token: str


class EmailVerificationRequest(BaseSchema):
    """Schema for email verification request."""

    token: str


class ResendVerificationRequest(BaseSchema):
    """Schema for resending verification email."""

    email: EmailStr


class PasswordResetRequest(BaseSchema):
    """Schema for requesting password reset."""

    email: EmailStr


class PasswordResetConfirm(BaseSchema):
    """Schema for confirming password reset with token."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class PasswordChangeRequest(BaseSchema):
    """Schema for changing password (when logged in)."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class LogoutRequest(BaseSchema):
    """Schema for logout request (optional refresh token)."""

    refresh_token: Optional[str] = None


# UserProfile Schemas
class UserProfileBase(BaseSchema):
    """Base user profile schema."""

    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(M|F|Other|Prefer not to say)$")
    height_cm: Optional[float] = Field(None, gt=0, le=300)
    current_weight_kg: Optional[float] = Field(None, gt=0, le=500)
    activity_level: Optional[str] = Field(
        None,
        pattern="^(sedentary|light|moderate|active|very_active)$",
    )
    dietary_restrictions: Optional[List[str]] = Field(default_factory=list)
    allergies: Optional[List[str]] = Field(default_factory=list)
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UserProfileCreate(UserProfileBase):
    """Schema for creating user profile."""

    pass


class UserProfileUpdate(UserProfileBase):
    """Schema for updating user profile."""

    pass


class UserProfileResponse(UserProfileBase, TimestampSchema):
    """Schema for user profile responses."""

    id: int
    user_id: int


# UserGoal Schemas
class UserGoalBase(BaseSchema):
    """Base user goal schema."""

    goal_type: str = Field(
        ...,
        pattern="^(weight_loss|weight_gain|maintain|muscle_gain)$",
    )
    target_weight_kg: Optional[float] = Field(None, gt=0, le=500)
    target_calories: Optional[int] = Field(None, gt=0, le=10000)
    macro_targets: Optional[Dict[str, float]] = None
    start_date: date
    target_date: Optional[date] = None
    status: str = Field(
        default="active",
        pattern="^(active|completed|paused|abandoned)$",
    )

    @field_validator("target_date")
    @classmethod
    def validate_target_date(cls, v: Optional[date], info) -> Optional[date]:
        """Ensure target_date is after start_date."""
        if v and "start_date" in info.data:
            start_date = info.data["start_date"]
            if v <= start_date:
                raise ValueError("target_date must be after start_date")
        return v


class UserGoalCreate(UserGoalBase):
    """Schema for creating user goal."""

    pass


class UserGoalUpdate(BaseSchema):
    """Schema for updating user goal."""

    goal_type: Optional[str] = Field(
        None,
        pattern="^(weight_loss|weight_gain|maintain|muscle_gain)$",
    )
    target_weight_kg: Optional[float] = Field(None, gt=0, le=500)
    target_calories: Optional[int] = Field(None, gt=0, le=10000)
    macro_targets: Optional[Dict[str, float]] = None
    target_date: Optional[date] = None
    status: Optional[str] = Field(
        None,
        pattern="^(active|completed|paused|abandoned)$",
    )


class UserGoalResponse(UserGoalBase, TimestampSchema):
    """Schema for user goal responses."""

    id: int
    user_id: int


# Combined User Response with Profile and Goals
class UserFullResponse(UserResponse):
    """Complete user response with profile and goals."""

    profile: Optional[UserProfileResponse] = None
    goals: List[UserGoalResponse] = Field(default_factory=list)
