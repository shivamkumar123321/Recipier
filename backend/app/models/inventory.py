"""
Inventory and food category models.

Includes InventoryItem and FoodCategory models.
"""

from datetime import date
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Column,
    Date,
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
    from app.models.recipe import RecipeIngredient
    from app.models.grocery import GroceryListItem


class FoodCategory(Base, TimestampMixin):
    """
    Food categories for organizing inventory, recipes, and grocery items.

    Attributes:
        id: Primary key
        name: Category name (unique)
        description: Category description
        icon: Icon identifier (emoji or icon name)
    """

    __tablename__ = "food_categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Category name",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Category description",
    )
    icon: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Icon identifier (emoji or icon name)",
    )

    # Relationships
    inventory_items: Mapped[List["InventoryItem"]] = relationship(
        "InventoryItem",
        back_populates="category",
    )
    recipe_ingredients: Mapped[List["RecipeIngredient"]] = relationship(
        "RecipeIngredient",
        back_populates="category",
    )
    grocery_list_items: Mapped[List["GroceryListItem"]] = relationship(
        "GroceryListItem",
        back_populates="category",
    )

    def __repr__(self) -> str:
        return f"<FoodCategory(id={self.id}, name='{self.name}')>"


class InventoryItem(Base, TimestampMixin, SoftDeleteMixin):
    """
    User pantry/fridge inventory tracking.

    Tracks what ingredients users have at home with quantities and expiration dates.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        category_id: Foreign key to food_categories table
        name: Item name
        quantity: Current quantity
        unit: Unit of measurement (g/oz/L/pieces)
        expiration_date: Expiration date (nullable)
        storage_location: Where item is stored (pantry/fridge/freezer)
        barcode: Barcode for scanning (nullable)
        nutrition_per_unit: Nutrition info per unit (JSONB)
    """

    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("food_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Item name",
    )
    quantity: Mapped[float] = mapped_column(
        Numeric(8, 2),
        nullable=False,
        comment="Current quantity",
    )
    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Unit of measurement",
    )
    expiration_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        index=True,
        comment="Expiration date",
    )
    storage_location: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="pantry/fridge/freezer",
    )
    barcode: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Barcode for scanning",
    )
    nutrition_per_unit: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Nutrition info per unit",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="inventory_items")
    category: Mapped[Optional["FoodCategory"]] = relationship(
        "FoodCategory",
        back_populates="inventory_items",
    )

    def __repr__(self) -> str:
        return f"<InventoryItem(id={self.id}, name='{self.name}', quantity={self.quantity} {self.unit})>"
