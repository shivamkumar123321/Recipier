"""
Meal planning models.

Includes MealPlan and MealPlanItem models for daily/weekly meal planning.
"""

from datetime import date
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.recipe import Recipe
    from app.models.grocery import GroceryList


class MealPlan(Base, TimestampMixin):
    """
    Meal planning model for weekly/daily meal organization.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        name: Plan name (e.g., "Week of Jan 15", "Keto Week 1")
        start_date: Plan start date
        end_date: Plan end date
        target_calories: Daily calorie target
        macro_targets: Daily macro targets (JSONB)
        status: Plan status (active/completed/archived)
    """

    __tablename__ = "meal_plans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Plan name",
    )
    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Plan start date",
    )
    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Plan end date",
    )
    target_calories: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Daily calorie target",
    )
    macro_targets: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Daily macro targets",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
        index=True,
        comment="active/completed/archived",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="meal_plans")
    meal_plan_items: Mapped[List["MealPlanItem"]] = relationship(
        "MealPlanItem",
        back_populates="meal_plan",
        cascade="all, delete-orphan",
    )
    grocery_lists: Mapped[List["GroceryList"]] = relationship(
        "GroceryList",
        back_populates="meal_plan",
    )

    def __repr__(self) -> str:
        return f"<MealPlan(id={self.id}, name='{self.name}', {self.start_date} to {self.end_date})>"


class MealPlanItem(Base, TimestampMixin):
    """
    Individual meals scheduled in meal plans.

    Attributes:
        id: Primary key
        meal_plan_id: Foreign key to meal_plans table
        recipe_id: Foreign key to recipes table (nullable)
        scheduled_date: Date scheduled
        meal_type: Type of meal (breakfast/lunch/dinner/snack)
        servings: Number of servings
        notes: Meal-specific notes
        is_completed: Whether meal was consumed
    """

    __tablename__ = "meal_plan_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    meal_plan_id: Mapped[int] = mapped_column(
        ForeignKey("meal_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipe_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("recipes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    scheduled_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Date scheduled",
    )
    meal_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="breakfast/lunch/dinner/snack",
    )
    servings: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Number of servings",
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Meal-specific notes",
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Meal consumed",
    )

    # Relationships
    meal_plan: Mapped["MealPlan"] = relationship(
        "MealPlan",
        back_populates="meal_plan_items",
    )
    recipe: Mapped[Optional["Recipe"]] = relationship(
        "Recipe",
        back_populates="meal_plan_items",
    )

    def __repr__(self) -> str:
        return f"<MealPlanItem(id={self.id}, date={self.scheduled_date}, meal_type='{self.meal_type}')>"
