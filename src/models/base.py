from datetime import datetime
from typing import Any
import uuid

from sqlalchemy import DateTime, func, text, types, FetchedValue
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    Inherits from DeclarativeBase (SQLAlchemy 2.0+ standard).
    
    Base.metadata acts as the central catalog holding DDL schema definitions 
    that Alembic inspects to automatically generate database migrations.
    """

    def to_dict(self) -> dict[str, any]:
        """Utility method to convert an ORM model instance into a Python dictionary."""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

# ---------------------------------------------------------
# Modular Mixin
# ---------------------------------------------------------

class UUIDMixin:
    """
    Mixin that adds a server-generated UUID v4 primary key.
    Uses PostgreSQL native 'gen_random_uuid()' function.
    """
    id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid,
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )


class TimestampMixin:
    """Mixin that adds timezone-aware created_at and updated_at columns."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=FetchedValue(),
        nullable=False
    )

# ---------------------------------------------------------
# Combined base model
# ---------------------------------------------------------

class BaseModel(Base, UUIDMixin, TimestampMixin):
    """
    Abstract Master Model combining UUID + Timestamps.
    Inherit from this for 95% of standard domain entities (User, Product, Document, etc.).
    """
    __abstract__ = True


