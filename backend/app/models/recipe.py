"""
Recipe-related database models.

Includes Recipe, RecipeIngredient, RecipeInstruction, and UserRecipe models.
"""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.inventory import FoodCategory
    from app.models.meal_plan import MealPlanItem


class Recipe(Base, TimestampMixin, SoftDeleteMixin):
    """
    Recipe storage model.

    Stores recipes (user-created or system/curated recipes).

    Attributes:
        id: Primary key
        user_id: Foreign key to users (NULL for system recipes)
        name: Recipe name
        description: Recipe description
        prep_time_minutes: Preparation time in minutes
        cook_time_minutes: Cooking time in minutes
        servings: Number of servings
        difficulty: Difficulty level (easy/medium/hard)
        image_url: Recipe image URL
        calories_per_serving: Calories per serving
        macros_per_serving: Macros per serving (JSONB)
        is_public: Whether recipe is public (for sharing)
        views_count: Number of views
        saves_count: Number of saves/favorites
    """

    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="NULL for system recipes",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Recipe name",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Recipe description",
    )
    prep_time_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Preparation time",
    )
    cook_time_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Cooking time",
    )
    servings: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Number of servings",
    )
    difficulty: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="easy/medium/hard",
    )
    image_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Recipe image URL",
    )
    calories_per_serving: Mapped[Optional[float]] = mapped_column(
        Numeric(7, 2),
        nullable=True,
        comment="Calories per serving",
    )
    macros_per_serving: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Macros per serving",
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Public/private recipe",
    )
    views_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="View count",
    )
    saves_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        index=True,
        comment="Save count",
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="recipes")
    ingredients: Mapped[List["RecipeIngredient"]] = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeIngredient.order_index",
    )
    instructions: Mapped[List["RecipeInstruction"]] = relationship(
        "RecipeInstruction",
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeInstruction.step_number",
    )
    saved_by_users: Mapped[List["UserRecipe"]] = relationship(
        "UserRecipe",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    meal_plan_items: Mapped[List["MealPlanItem"]] = relationship(
        "MealPlanItem",
        back_populates="recipe",
    )

    def __repr__(self) -> str:
        return f"<Recipe(id={self.id}, name='{self.name}', servings={self.servings})>"


class RecipeIngredient(Base, TimestampMixin):
    """
    Ingredients required for recipes.

    Attributes:
        id: Primary key
        recipe_id: Foreign key to recipes table
        category_id: Foreign key to food_categories table
        ingredient_name: Name of the ingredient
        quantity: Amount needed
        unit: Unit of measurement
        is_optional: Whether ingredient is optional
        order_index: Display order
    """

    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("food_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    ingredient_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Ingredient name",
    )
    quantity: Mapped[float] = mapped_column(
        Numeric(8, 2),
        nullable=False,
        comment="Amount needed",
    )
    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Unit of measurement",
    )
    is_optional: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Optional ingredient",
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Display order",
    )

    # Relationships
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="ingredients")
    category: Mapped[Optional["FoodCategory"]] = relationship(
        "FoodCategory",
        back_populates="recipe_ingredients",
    )

    def __repr__(self) -> str:
        return f"<RecipeIngredient(id={self.id}, ingredient='{self.ingredient_name}', quantity={self.quantity} {self.unit})>"


class RecipeInstruction(Base, TimestampMixin):
    """
    Step-by-step cooking instructions for recipes.

    Attributes:
        id: Primary key
        recipe_id: Foreign key to recipes table
        step_number: Step order (1, 2, 3, ...)
        instruction: Instruction text
        duration_minutes: Time for this step (optional)
        image_url: Step image URL (optional)
    """

    __tablename__ = "recipe_instructions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Step order",
    )
    instruction: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Instruction text",
    )
    duration_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Time for this step",
    )
    image_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Step image URL",
    )

    # Relationships
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="instructions")

    def __repr__(self) -> str:
        return f"<RecipeInstruction(id={self.id}, recipe_id={self.recipe_id}, step={self.step_number})>"


class UserRecipe(Base, TimestampMixin):
    """
    User-saved/favorited recipes with ratings and notes.

    Junction table between users and recipes with additional data.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        recipe_id: Foreign key to recipes table
        notes: User's personal notes
        rating: Rating 1-5
    """

    __tablename__ = "user_recipes"

    __table_args__ = (
        UniqueConstraint("user_id", "recipe_id", name="uq_user_recipe"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User's personal notes",
    )
    rating: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Rating 1-5",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="saved_recipes")
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="saved_by_users")

    def __repr__(self) -> str:
        return f"<UserRecipe(id={self.id}, user_id={self.user_id}, recipe_id={self.recipe_id}, rating={self.rating})>"
