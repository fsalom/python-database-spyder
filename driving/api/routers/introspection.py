"""FastAPI router for database introspection."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from driven.db.connections.adapter import ConnectionsDBRepositoryAdapter
from driven.db.metadata.adapter import MetadataDBRepositoryAdapter
from application.services.introspection_service import IntrospectionService
from application.services.connections_service import ConnectionsService
from driving.api.schemas.introspection_schemas import (
    DiscoveredTableResponse,
    DiscoveredRelationResponse,
    IntrospectionRequest,
    IntrospectionResponse,
)

router = APIRouter(prefix="/introspection", tags=["introspection"])


def get_introspection_service(
    db: AsyncSession = Depends(get_db),
) -> IntrospectionService:
    """Dependency to get introspection service."""
    metadata_repo = MetadataDBRepositoryAdapter(db)
    return IntrospectionService(metadata_repo)


def get_connections_service(
    db: AsyncSession = Depends(get_db),
) -> ConnectionsService:
    """Dependency to get connections service."""
    connections_repo = ConnectionsDBRepositoryAdapter(db)
    metadata_repo = MetadataDBRepositoryAdapter(db)
    return ConnectionsService(connections_repo, metadata_repo)


@router.post("", response_model=IntrospectionResponse)
async def introspect_database(
    request: IntrospectionRequest,
    introspection_service: IntrospectionService = Depends(get_introspection_service),
    connections_service: ConnectionsService = Depends(get_connections_service),
):
    """
    Introspect a database and save discovered metadata.
    This replaces any existing metadata for the connection.
    """
    # Get connection
    connection = await connections_service.get_connection_by_id(request.connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection with id {request.connection_id} not found",
        )

    try:
        # Perform introspection
        tables, relations = await introspection_service.introspect_database(connection)

        # Update last introspection timestamp
        await connections_service.update_last_introspection(request.connection_id)

        return IntrospectionResponse(
            success=True,
            message=f"Successfully introspected database '{connection.name}'",
            tables_count=len(tables),
            relations_count=len(relations),
        )
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Introspection failed: {str(e)}",
        )


@router.get("/connections/{connection_id}/tables", response_model=List[DiscoveredTableResponse])
async def get_tables_by_connection(
    connection_id: int,
    service: IntrospectionService = Depends(get_introspection_service),
):
    """Get all discovered tables for a connection."""
    tables = await service.get_tables_by_connection(connection_id)
    return [DiscoveredTableResponse.model_validate(table) for table in tables]


@router.get("/tables/{table_id}", response_model=DiscoveredTableResponse)
async def get_table(
    table_id: int,
    service: IntrospectionService = Depends(get_introspection_service),
):
    """Get a specific discovered table by ID."""
    try:
        table = await service.get_table_by_id(table_id)
        return DiscoveredTableResponse.model_validate(table)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/connections/{connection_id}/relations", response_model=List[DiscoveredRelationResponse])
async def get_relations_by_connection(
    connection_id: int,
    service: IntrospectionService = Depends(get_introspection_service),
):
    """Get all discovered relations for a connection."""
    relations = await service.get_relations_by_connection(connection_id)
    return [DiscoveredRelationResponse.model_validate(rel) for rel in relations]


@router.post("/connections/{connection_id}/refresh", response_model=IntrospectionResponse)
async def refresh_metadata(
    connection_id: int,
    introspection_service: IntrospectionService = Depends(get_introspection_service),
    connections_service: ConnectionsService = Depends(get_connections_service),
):
    """
    Refresh metadata for a connection by re-introspecting the database.
    This replaces all existing metadata.
    """
    # Get connection
    connection = await connections_service.get_connection_by_id(connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection with id {connection_id} not found",
        )

    try:
        # Refresh metadata
        tables, relations = await introspection_service.refresh_metadata(connection)

        # Update last introspection timestamp
        await connections_service.update_last_introspection(connection_id)

        return IntrospectionResponse(
            success=True,
            message=f"Successfully refreshed metadata for '{connection.name}'",
            tables_count=len(tables),
            relations_count=len(relations),
        )
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Refresh failed: {str(e)}",
        )


@router.delete("/connections/{connection_id}/metadata", status_code=status.HTTP_204_NO_CONTENT)
async def delete_metadata(
    connection_id: int,
    service: IntrospectionService = Depends(get_introspection_service),
):
    """Delete all metadata for a connection."""
    await service.delete_metadata(connection_id)
