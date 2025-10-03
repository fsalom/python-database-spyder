"""Connection domain entities."""

from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class DatabaseType(str, Enum):
    """Supported database types."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MSSQL = "mssql"
    ORACLE = "oracle"


class ConnectionStatus(str, Enum):
    """Connection status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"


class Connection(BaseModel):
    """Connection domain entity."""

    id: Optional[int] = None
    name: str = Field(..., description="Friendly name for the connection")
    database_type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    password: str = Field(..., description="Encrypted password")
    db_schema: Optional[str] = Field(None, description="Database schema (for PostgreSQL, etc.)")
    ssl_enabled: bool = False
    status: ConnectionStatus = ConnectionStatus.INACTIVE
    last_introspection: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class ConnectionCreate(BaseModel):
    """Connection creation request."""

    name: str
    database_type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    password: str
    db_schema: Optional[str] = None
    ssl_enabled: bool = False


class ConnectionUpdate(BaseModel):
    """Connection update request."""

    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    db_schema: Optional[str] = None
    ssl_enabled: Optional[bool] = None
    status: Optional[ConnectionStatus] = None
