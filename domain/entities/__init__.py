"""Domain entities."""

from domain.entities.users import User, BaseUser, Department
from domain.entities.connection import (
    Connection,
    ConnectionCreate,
    ConnectionUpdate,
    DatabaseType,
    ConnectionStatus,
)
from domain.entities.discovered_table import (
    DiscoveredTable,
    DiscoveredColumn,
    DiscoveredRelation,
    RelationType,
)
from domain.entities.api_endpoint import (
    ApiEndpoint,
    ApiEndpointCreate,
    ApiEndpointUpdate,
    ApiEndpointConfig,
    EndpointTableConfig,
    EndpointRelationConfig,
    HttpMethod,
    ApiEndpointStatus,
)

__all__ = [
    # Users
    "User",
    "BaseUser",
    "Department",
    # Connections
    "Connection",
    "ConnectionCreate",
    "ConnectionUpdate",
    "DatabaseType",
    "ConnectionStatus",
    # Discovered metadata
    "DiscoveredTable",
    "DiscoveredColumn",
    "DiscoveredRelation",
    "RelationType",
    # API Endpoints
    "ApiEndpoint",
    "ApiEndpointCreate",
    "ApiEndpointUpdate",
    "ApiEndpointConfig",
    "EndpointTableConfig",
    "EndpointRelationConfig",
    "HttpMethod",
    "ApiEndpointStatus",
]
