"""Discovered metadata database models using SQLAlchemy."""

from datetime import datetime
from typing import List
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from config.database import Base


class DiscoveredTableDBO(Base):
    """Discovered table database model."""

    __tablename__ = "discovered_tables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("connections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    table_name: Mapped[str] = mapped_column(String(255), nullable=False)
    schema_name: Mapped[str] = mapped_column(String(255), nullable=True)
    table_type: Mapped[str] = mapped_column(String(50), default="TABLE", nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    columns: Mapped[List["DiscoveredColumnDBO"]] = relationship(
        "DiscoveredColumnDBO",
        back_populates="table",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<DiscoveredTableDBO(id={self.id}, name='{self.table_name}')>"


class DiscoveredColumnDBO(Base):
    """Discovered column database model."""

    __tablename__ = "discovered_columns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    table_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("discovered_tables.id", ondelete="CASCADE"), nullable=False, index=True
    )
    column_name: Mapped[str] = mapped_column(String(255), nullable=False)
    data_type: Mapped[str] = mapped_column(String(100), nullable=False)
    is_nullable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_primary_key: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_foreign_key: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    default_value: Mapped[str] = mapped_column(Text, nullable=True)
    max_length: Mapped[int] = mapped_column(Integer, nullable=True)
    precision: Mapped[int] = mapped_column(Integer, nullable=True)
    scale: Mapped[int] = mapped_column(Integer, nullable=True)
    ordinal_position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    table: Mapped["DiscoveredTableDBO"] = relationship(
        "DiscoveredTableDBO",
        back_populates="columns"
    )

    def __repr__(self) -> str:
        return f"<DiscoveredColumnDBO(id={self.id}, name='{self.column_name}', type='{self.data_type}')>"


class DiscoveredRelationDBO(Base):
    """Discovered relationship database model."""

    __tablename__ = "discovered_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_table_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("discovered_tables.id", ondelete="CASCADE"), nullable=False, index=True
    )
    to_table_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("discovered_tables.id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_column_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("discovered_columns.id", ondelete="CASCADE"), nullable=False
    )
    to_column_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("discovered_columns.id", ondelete="CASCADE"), nullable=False
    )
    relation_type: Mapped[str] = mapped_column(String(50), default="many_to_one", nullable=False)
    constraint_name: Mapped[str] = mapped_column(String(255), nullable=True)
    on_delete: Mapped[str] = mapped_column(String(50), default="NO ACTION", nullable=False)
    on_update: Mapped[str] = mapped_column(String(50), default="NO ACTION", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<DiscoveredRelationDBO(id={self.id}, from_table={self.from_table_id}, to_table={self.to_table_id})>"
