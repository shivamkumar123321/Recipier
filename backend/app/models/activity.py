"""
Activity logging model for audit trails.

Tracks user actions and changes for security and analytics.
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class ActivityLog(Base, TimestampMixin):
    """
    Activity and audit log for tracking user actions.

    Records important user actions for security, debugging, and analytics.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table (nullable for system events)
        activity_type: Type of activity (create/update/delete/login/etc.)
        entity_type: Type of entity affected (meal/recipe/inventory_item/etc.)
        entity_id: ID of affected entity
        changes: Before/after data for updates (JSONB)
        ip_address: User IP address (IPv6 compatible)
        created_at: Activity timestamp
    """

    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="NULL for system events",
    )
    activity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="create/update/delete/login/logout",
    )
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="meal/recipe/inventory_item/user/etc.",
    )
    entity_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="ID of affected entity",
    )
    changes: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Before/after data for updates",
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="User IP address (IPv6 compatible)",
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="activity_logs")

    def __repr__(self) -> str:
        return f"<ActivityLog(id={self.id}, type='{self.activity_type}', entity='{self.entity_type}:{self.entity_id}')>"
