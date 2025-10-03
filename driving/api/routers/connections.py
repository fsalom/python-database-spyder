"""FastAPI router for connections management."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from domain.entities.connection import Connection
from driven.db.connections.adapter import ConnectionsDBRepositoryAdapter
from driven.db.metadata.adapter import MetadataDBRepositoryAdapter
from application.services.connections_service import ConnectionsService
from infrastructure.inspectors.inspector_factory import InspectorFactory
from driving.api.schemas.connection_schemas import (
    ConnectionCreate,
    ConnectionUpdate,
    ConnectionResponse,
    ConnectionTestRequest,
    ConnectionTestResponse,
)

router = APIRouter(prefix="/connections", tags=["connections"])


def get_connections_service(
    db: AsyncSession = Depends(get_db),
) -> ConnectionsService:
    """Dependency to get connections service."""
    connections_repo = ConnectionsDBRepositoryAdapter(db)
    metadata_repo = MetadataDBRepositoryAdapter(db)
    return ConnectionsService(connections_repo, metadata_repo)


@router.post("", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection(
    connection_data: ConnectionCreate,
    service: ConnectionsService = Depends(get_connections_service),
):
    """Create a new database connection."""
    try:
        connection = Connection(
            name=connection_data.name,
            database_type=connection_data.database_type,
            host=connection_data.host,
            port=connection_data.port,
            database=connection_data.database,
            username=connection_data.username,
            password=connection_data.password,
            db_schema=connection_data.db_schema,
            ssl_enabled=connection_data.ssl_enabled,
        )
        saved_connection = await service.create_connection(connection)
        return ConnectionResponse.model_validate(saved_connection)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[ConnectionResponse])
async def get_all_connections(
    service: ConnectionsService = Depends(get_connections_service),
):
    """Get all database connections."""
    connections = await service.get_all_connections()
    return [ConnectionResponse.model_validate(conn) for conn in connections]


@router.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(
    connection_id: int,
    service: ConnectionsService = Depends(get_connections_service),
):
    """Get a connection by ID."""
    connection = await service.get_connection_by_id(connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection with id {connection_id} not found",
        )
    return ConnectionResponse.model_validate(connection)


@router.put("/{connection_id}", response_model=ConnectionResponse)
async def update_connection(
    connection_id: int,
    connection_data: ConnectionUpdate,
    service: ConnectionsService = Depends(get_connections_service),
):
    """Update an existing connection."""
    # Get existing connection
    existing = await service.get_connection_by_id(connection_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection with id {connection_id} not found",
        )

    # Update only provided fields
    update_dict = connection_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(existing, field, value)

    try:
        updated_connection = await service.update_connection(existing)
        return ConnectionResponse.model_validate(updated_connection)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    connection_id: int,
    service: ConnectionsService = Depends(get_connections_service),
):
    """Delete a connection and all its metadata."""
    success = await service.delete_connection(connection_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection with id {connection_id} not found",
        )


@router.post("/test", response_model=ConnectionTestResponse)
async def test_connection(
    test_data: ConnectionTestRequest,
    service: ConnectionsService = Depends(get_connections_service),
):
    """Test a database connection without saving it."""
    connection = Connection(
        name=test_data.name,
        database_type=test_data.database_type,
        host=test_data.host,
        port=test_data.port,
        database=test_data.database,
        username=test_data.username,
        password=test_data.password,
        db_schema=test_data.db_schema,
        ssl_enabled=test_data.ssl_enabled,
    )

    inspector = InspectorFactory.create_inspector(connection)
    is_connected = await service.test_connection(connection, inspector)

    return ConnectionTestResponse(
        success=is_connected,
        message="Connection successful" if is_connected else "Connection failed",
    )
