"""User database models using SQLAlchemy."""

from datetime import datetime
from typing import List
from sqlalchemy import Boolean, String, DateTime, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from config.database import Base


# Association table for many-to-many relationship
user_department_association = Table(
    "user_department",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("department_id", Integer, ForeignKey("departments.id", ondelete="CASCADE"), primary_key=True),
)


class DepartmentDBO(Base):
    """Department database model."""

    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    users: Mapped[List["UserDBO"]] = relationship(
        "UserDBO",
        secondary=user_department_association,
        back_populates="departments"
    )

    def __repr__(self) -> str:
        return f"<DepartmentDBO(id={self.id}, name='{self.name}')>"


class UserDBO(Base):
    """User database model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=False, default="")
    last_name: Mapped[str] = mapped_column(String(150), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    departments: Mapped[List["DepartmentDBO"]] = relationship(
        "DepartmentDBO",
        secondary=user_department_association,
        back_populates="users"
    )

    def __repr__(self) -> str:
        return f"<UserDBO(id={self.id}, email='{self.email}')>"
