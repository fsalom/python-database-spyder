"""FastAPI router for dashboard statistics."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from config.database import get_db
from driven.db.connections.adapter import ConnectionsDBRepositoryAdapter
from driven.db.metadata.adapter import MetadataDBRepositoryAdapter
from application.services.connections_service import ConnectionsService
from application.services.introspection_service import IntrospectionService
from driving.api.schemas.connection_schemas import ConnectionResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardStats(BaseModel):
    """Dashboard statistics response."""

    total_connections: int
    active_connections: int
    inactive_connections: int
    error_connections: int
    total_tables: int
    total_relations: int


class DashboardResponse(BaseModel):
    """Dashboard data response."""

    stats: DashboardStats
    recent_connections: list[ConnectionResponse]


def get_connections_service(
    db: AsyncSession = Depends(get_db),
) -> ConnectionsService:
    """Dependency to get connections service."""
    connections_repo = ConnectionsDBRepositoryAdapter(db)
    metadata_repo = MetadataDBRepositoryAdapter(db)
    return ConnectionsService(connections_repo, metadata_repo)


def get_introspection_service(
    db: AsyncSession = Depends(get_db),
) -> IntrospectionService:
    """Dependency to get introspection service."""
    metadata_repo = MetadataDBRepositoryAdapter(db)
    return IntrospectionService(metadata_repo)


@router.get("", response_model=DashboardResponse)
async def get_dashboard_stats(
    connections_service: ConnectionsService = Depends(get_connections_service),
    introspection_service: IntrospectionService = Depends(get_introspection_service),
):
    """
    Get dashboard statistics and recent connections.
    """
    # Get all connections
    all_connections = await connections_service.get_all_connections()

    # Calculate statistics
    total_connections = len(all_connections)
    active_connections = sum(1 for c in all_connections if c.status == "active")
    inactive_connections = sum(1 for c in all_connections if c.status == "inactive")
    error_connections = sum(1 for c in all_connections if c.status == "error")

    # Count total tables and relations
    total_tables = 0
    total_relations = 0

    for connection in all_connections:
        tables = await introspection_service.get_tables_by_connection(connection.id)
        relations = await introspection_service.get_relations_by_connection(connection.id)
        total_tables += len(tables)
        total_relations += len(relations)

    # Get recent connections (last 5, sorted by last_introspection or created_at)
    sorted_connections = sorted(
        all_connections,
        key=lambda c: c.last_introspection or c.created_at,
        reverse=True
    )
    recent_connections = sorted_connections[:5]

    stats = DashboardStats(
        total_connections=total_connections,
        active_connections=active_connections,
        inactive_connections=inactive_connections,
        error_connections=error_connections,
        total_tables=total_tables,
        total_relations=total_relations,
    )

    return DashboardResponse(
        stats=stats,
        recent_connections=[ConnectionResponse.model_validate(c) for c in recent_connections]
    )
