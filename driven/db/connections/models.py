"""Connection database models using SQLAlchemy."""

from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from config.database import Base
from domain.entities.connection import DatabaseType, ConnectionStatus


class ConnectionDBO(Base):
    """Connection database model."""

    __tablename__ = "connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    database_type: Mapped[str] = mapped_column(
        SQLEnum(DatabaseType, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    database: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(500), nullable=False)  # Should be encrypted
    db_schema: Mapped[str] = mapped_column(String(255), nullable=True)
    ssl_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(
        SQLEnum(ConnectionStatus, values_callable=lambda x: [e.value for e in x]),
        default=ConnectionStatus.INACTIVE,
        nullable=False
    )
    last_introspection: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<ConnectionDBO(id={self.id}, name='{self.name}', type='{self.database_type}')>"
