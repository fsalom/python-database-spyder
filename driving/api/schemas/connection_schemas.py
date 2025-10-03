"""Pydantic schemas for Connection API."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from domain.entities.connection import DatabaseType, ConnectionStatus


class ConnectionCreate(BaseModel):
    """Schema for creating a new connection."""

    name: str = Field(..., min_length=1, max_length=255)
    database_type: DatabaseType
    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(..., gt=0, lt=65536)
    database: str = Field(..., min_length=1, max_length=255)
    username: str = Field(..., max_length=255)
    password: str = Field(..., max_length=500)
    db_schema: Optional[str] = Field(None, max_length=255)
    ssl_enabled: bool = False


class ConnectionUpdate(BaseModel):
    """Schema for updating a connection."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    database_type: Optional[DatabaseType] = None
    host: Optional[str] = Field(None, min_length=1, max_length=255)
    port: Optional[int] = Field(None, gt=0, lt=65536)
    database: Optional[str] = Field(None, min_length=1, max_length=255)
    username: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, max_length=500)
    db_schema: Optional[str] = Field(None, max_length=255)
    ssl_enabled: Optional[bool] = None
    status: Optional[ConnectionStatus] = None


class ConnectionResponse(BaseModel):
    """Schema for connection response."""

    id: int
    name: str
    database_type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    db_schema: Optional[str] = None
    ssl_enabled: bool
    status: ConnectionStatus
    last_introspection: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConnectionTestRequest(BaseModel):
    """Schema for testing a connection."""

    name: str = Field(..., min_length=1, max_length=255)
    database_type: DatabaseType
    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(..., gt=0, lt=65536)
    database: str = Field(..., min_length=1, max_length=255)
    username: str = Field(..., max_length=255)
    password: str = Field(..., max_length=500)
    db_schema: Optional[str] = Field(None, max_length=255)
    ssl_enabled: bool = False


class ConnectionTestResponse(BaseModel):
    """Schema for connection test response."""

    success: bool
    message: str
