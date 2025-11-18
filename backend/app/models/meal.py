"""
Meal-related database models.

Includes Meal, MealItem, and AIAnalysis models.
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Meal(Base, TimestampMixin, SoftDeleteMixin):
    """
    Meal logging model.

    Tracks user meals with nutrition data, supporting text, voice, and image input.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        name: Meal name/title
        meal_type: Type of meal (breakfast/lunch/dinner/snack)
        description: User-provided description
        consumed_at: When meal was consumed (user's local time)
        input_method: How meal was logged (text/voice/image)
        image_url: URL to meal photo (if provided)
        voice_transcript: Whisper transcription (if voice input)
        total_calories: Total calories for the meal
        macros: Macronutrient breakdown (JSONB)
        micronutrients: Micronutrient data (JSONB)
    """

    __tablename__ = "meals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Meal name/title",
    )
    meal_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="breakfast/lunch/dinner/snack",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User-provided description",
    )
    consumed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
        comment="When meal was consumed",
    )
    input_method: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="text/voice/image",
    )
    image_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="URL to meal photo",
    )
    voice_transcript: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Whisper transcription",
    )
    total_calories: Mapped[Optional[float]] = mapped_column(
        Numeric(7, 2),
        nullable=True,
        comment="Total calories",
    )
    macros: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Macronutrient breakdown",
    )
    micronutrients: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Micronutrient data",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="meals")
    meal_items: Mapped[List["MealItem"]] = relationship(
        "MealItem",
        back_populates="meal",
        cascade="all, delete-orphan",
    )
    ai_analysis: Mapped[Optional["AIAnalysis"]] = relationship(
        "AIAnalysis",
        back_populates="meal",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Meal(id={self.id}, name='{self.name}', consumed_at={self.consumed_at})>"


class MealItem(Base, TimestampMixin):
    """
    Individual food items within a meal.

    Attributes:
        id: Primary key
        meal_id: Foreign key to meals table
        food_name: Name of the food item
        quantity: Amount consumed
        unit: Unit of measurement (g/oz/cup/piece/serving)
        calories: Calories for this item
        nutrition_data: Detailed nutrition breakdown (JSONB)
    """

    __tablename__ = "meal_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    meal_id: Mapped[int] = mapped_column(
        ForeignKey("meals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    food_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Food item name",
    )
    quantity: Mapped[float] = mapped_column(
        Numeric(8, 2),
        nullable=False,
        comment="Amount consumed",
    )
    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Unit of measurement",
    )
    calories: Mapped[Optional[float]] = mapped_column(
        Numeric(7, 2),
        nullable=True,
        comment="Calories for this item",
    )
    nutrition_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Detailed nutrition breakdown",
    )

    # Relationships
    meal: Mapped["Meal"] = relationship("Meal", back_populates="meal_items")

    def __repr__(self) -> str:
        return f"<MealItem(id={self.id}, food='{self.food_name}', quantity={self.quantity} {self.unit})>"


class AIAnalysis(Base, TimestampMixin):
    """
    AI-generated nutrition analysis for meals.

    Stores GPT-4 analysis and recommendations for meals.

    Attributes:
        id: Primary key
        meal_id: Foreign key to meals table (one-to-one)
        analysis: GPT-4 nutrition analysis text
        recommendations: Personalized suggestions
        nutrition_breakdown: Structured nutrition data (JSONB)
        confidence_score: AI confidence level (0.00-1.00)
        model_version: OpenAI model version used
    """

    __tablename__ = "ai_analyses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    meal_id: Mapped[int] = mapped_column(
        ForeignKey("meals.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    analysis: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="GPT-4 nutrition analysis",
    )
    recommendations: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Personalized suggestions",
    )
    nutrition_breakdown: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Structured nutrition data",
    )
    confidence_score: Mapped[Optional[float]] = mapped_column(
        Numeric(3, 2),
        nullable=True,
        comment="AI confidence (0.00-1.00)",
    )
    model_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="OpenAI model version",
    )

    # Relationships
    meal: Mapped["Meal"] = relationship("Meal", back_populates="ai_analysis")

    def __repr__(self) -> str:
        return f"<AIAnalysis(id={self.id}, meal_id={self.meal_id}, confidence={self.confidence_score})>"
