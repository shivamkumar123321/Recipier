"""
Database base configuration for SQLAlchemy models.

This module provides the declarative base class and common mixins
for all database models.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """
    Base class for all database models.

    Provides common functionality and configuration for all models.
    """

    # Generate __tablename__ automatically from class name
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table name from class name (snake_case)."""
        # Convert CamelCase to snake_case
        name = cls.__name__
        return "".join(
            ["_" + c.lower() if c.isupper() else c for c in name]
        ).lstrip("_")


class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamps to models.

    Automatically sets created_at on insert and updates updated_at on modification.
    """

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Record creation timestamp (UTC)",
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp (UTC)",
    )


class SoftDeleteMixin:
    """
    Mixin to add soft delete functionality.

    Instead of deleting records, sets deleted_at timestamp.
    Query filters should exclude records where deleted_at IS NOT NULL.
    """

    deleted_at = Column(
        DateTime,
        nullable=True,
        default=None,
        comment="Soft delete timestamp (UTC)",
    )

    def soft_delete(self) -> None:
        """Mark this record as deleted."""
        self.deleted_at = datetime.utcnow()

    @property
    def is_deleted(self) -> bool:
        """Check if this record is soft deleted."""
        return self.deleted_at is not None
