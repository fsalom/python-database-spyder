"""API Endpoint domain entities."""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class HttpMethod(str, Enum):
    """HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class ApiEndpointStatus(str, Enum):
    """API Endpoint status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


class ApiEndpoint(BaseModel):
    """API Endpoint domain entity."""

    id: Optional[int] = None
    name: str = Field(..., description="Friendly name for the endpoint")
    path: str = Field(..., description="API path (e.g., /api/users)")
    method: HttpMethod
    description: Optional[str] = None
    connection_id: int
    status: ApiEndpointStatus = ApiEndpointStatus.DRAFT

    # Configuration (stored as JSON in DB)
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Endpoint configuration including tables, columns, filters, etc."
    )

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None  # User ID

    class Config:
        from_attributes = True
        use_enum_values = True


class EndpointTableConfig(BaseModel):
    """Configuration for a table in an endpoint."""

    table_id: int
    table_name: str
    alias: Optional[str] = None
    selected_columns: List[str] = Field(default_factory=list, description="Column names to include")
    filters: Dict[str, Any] = Field(default_factory=dict, description="WHERE clause filters")
    order_by: List[str] = Field(default_factory=list, description="ORDER BY columns")
    limit: Optional[int] = None
    offset: Optional[int] = None


class EndpointRelationConfig(BaseModel):
    """Configuration for a relation in an endpoint."""

    relation_id: int
    include_related: bool = True
    selected_columns: List[str] = Field(default_factory=list, description="Columns from related table")


class ApiEndpointConfig(BaseModel):
    """Full configuration for an API endpoint."""

    main_table: EndpointTableConfig
    relations: List[EndpointRelationConfig] = []
    enable_pagination: bool = True
    page_size: int = 50
    max_page_size: int = 1000
    enable_filtering: bool = True
    enable_sorting: bool = True
    require_authentication: bool = False


class ApiEndpointCreate(BaseModel):
    """API Endpoint creation request."""

    name: str
    path: str
    method: HttpMethod
    description: Optional[str] = None
    connection_id: int
    config: ApiEndpointConfig


class ApiEndpointUpdate(BaseModel):
    """API Endpoint update request."""

    name: Optional[str] = None
    path: Optional[str] = None
    method: Optional[HttpMethod] = None
    description: Optional[str] = None
    status: Optional[ApiEndpointStatus] = None
    config: Optional[ApiEndpointConfig] = None
