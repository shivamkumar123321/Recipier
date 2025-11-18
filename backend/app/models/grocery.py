"""
Grocery list models.

Includes GroceryList and GroceryListItem models for shopping management.
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
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.meal_plan import MealPlan
    from app.models.inventory import FoodCategory


class GroceryList(Base, TimestampMixin):
    """
    Shopping list model (auto-generated or manual).

    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        meal_plan_id: Foreign key to meal_plans table (nullable for manual lists)
        name: List name
        status: List status (active/completed/archived)
    """

    __tablename__ = "grocery_lists"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    meal_plan_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("meal_plans.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="NULL for manual lists",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="List name",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
        comment="active/completed/archived",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="grocery_lists")
    meal_plan: Mapped[Optional["MealPlan"]] = relationship(
        "MealPlan",
        back_populates="grocery_lists",
    )
    items: Mapped[List["GroceryListItem"]] = relationship(
        "GroceryListItem",
        back_populates="grocery_list",
        cascade="all, delete-orphan",
        order_by="GroceryListItem.order_index",
    )

    def __repr__(self) -> str:
        return f"<GroceryList(id={self.id}, name='{self.name}', status='{self.status}')>"


class GroceryListItem(Base, TimestampMixin):
    """
    Individual items in grocery lists.

    Attributes:
        id: Primary key
        grocery_list_id: Foreign key to grocery_lists table
        category_id: Foreign key to food_categories table
        item_name: Item name
        quantity: Quantity to buy
        unit: Unit of measurement
        is_checked: Whether item was purchased
        estimated_price: Estimated price (optional)
        notes: Item-specific notes
        order_index: Display order
    """

    __tablename__ = "grocery_list_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    grocery_list_id: Mapped[int] = mapped_column(
        ForeignKey("grocery_lists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("food_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    item_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Item name",
    )
    quantity: Mapped[float] = mapped_column(
        Numeric(8, 2),
        nullable=False,
        comment="Quantity to buy",
    )
    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Unit of measurement",
    )
    is_checked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Item purchased",
    )
    estimated_price: Mapped[Optional[float]] = mapped_column(
        Numeric(8, 2),
        nullable=True,
        comment="Estimated price",
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Item-specific notes",
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Display order",
    )

    # Relationships
    grocery_list: Mapped["GroceryList"] = relationship(
        "GroceryList",
        back_populates="items",
    )
    category: Mapped[Optional["FoodCategory"]] = relationship(
        "FoodCategory",
        back_populates="grocery_list_items",
    )

    def __repr__(self) -> str:
        return f"<GroceryListItem(id={self.id}, item='{self.item_name}', quantity={self.quantity} {self.unit})>"
