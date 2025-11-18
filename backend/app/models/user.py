"""
User-related database models.

Includes User, UserProfile, and UserGoal models.
"""

from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.meal import Meal
    from app.models.inventory import InventoryItem
    from app.models.recipe import Recipe, UserRecipe
    from app.models.meal_plan import MealPlan
    from app.models.grocery import GroceryList
    from app.models.activity import ActivityLog


class User(Base, TimestampMixin, SoftDeleteMixin):
    """
    User account model for authentication and core user data.

    Attributes:
        id: Primary key
        email: Unique email address (lowercase)
        hashed_password: Bcrypt hashed password
        is_active: Account active status
        is_verified: Email verification status
        created_at: Account creation timestamp
        updated_at: Last modification timestamp
        deleted_at: Soft delete timestamp
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="User email address (lowercase)",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Bcrypt hashed password",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Account active status",
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Email verification status",
    )

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    goals: Mapped[List["UserGoal"]] = relationship(
        "UserGoal",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    meals: Mapped[List["Meal"]] = relationship(
        "Meal",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    inventory_items: Mapped[List["InventoryItem"]] = relationship(
        "InventoryItem",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    recipes: Mapped[List["Recipe"]] = relationship(
        "Recipe",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    saved_recipes: Mapped[List["UserRecipe"]] = relationship(
        "UserRecipe",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    meal_plans: Mapped[List["MealPlan"]] = relationship(
        "MealPlan",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    grocery_lists: Mapped[List["GroceryList"]] = relationship(
        "GroceryList",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    activity_logs: Mapped[List["ActivityLog"]] = relationship(
        "ActivityLog",
        back_populates="user",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"


class UserProfile(Base, TimestampMixin):
    """
    Extended user profile information.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table (one-to-one)
        full_name: User's full name
        date_of_birth: Date of birth for age calculations
        gender: Gender (M/F/Other/Prefer not to say)
        height_cm: Height in centimeters
        current_weight_kg: Current weight in kilograms
        activity_level: Activity level for calorie calculations
        dietary_restrictions: List of dietary restrictions (JSONB)
        allergies: List of allergies (JSONB)
        preferences: Flexible preferences object (JSONB)
    """

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="M/F/Other/Prefer not to say",
    )
    height_cm: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Height in centimeters",
    )
    current_weight_kg: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Current weight in kilograms",
    )
    activity_level: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="sedentary/light/moderate/active/very_active",
    )
    dietary_restrictions: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        default=list,
        nullable=True,
        comment="List of dietary restrictions",
    )
    allergies: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        default=list,
        nullable=True,
        comment="List of food allergies",
    )
    preferences: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True,
        comment="Flexible user preferences",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")

    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, name='{self.full_name}')>"


class UserGoal(Base, TimestampMixin):
    """
    User health and fitness goals.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        goal_type: Type of goal (weight_loss/weight_gain/maintain/muscle_gain)
        target_weight_kg: Target weight in kilograms
        target_calories: Daily calorie target
        macro_targets: Macro nutrient targets (JSONB)
        start_date: Goal start date
        target_date: Expected completion date
        status: Goal status (active/completed/paused/abandoned)
    """

    __tablename__ = "user_goals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    goal_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="weight_loss/weight_gain/maintain/muscle_gain",
    )
    target_weight_kg: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    target_calories: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Daily calorie target",
    )
    macro_targets: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Macro nutrient targets (protein, carbs, fat)",
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
        comment="active/completed/paused/abandoned",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="goals")

    def __repr__(self) -> str:
        return f"<UserGoal(id={self.id}, user_id={self.user_id}, type='{self.goal_type}')>"
