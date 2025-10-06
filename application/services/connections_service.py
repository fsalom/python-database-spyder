"""Connections management service."""

from typing import List, Optional
from datetime import datetime

from domain.entities.connection import Connection, ConnectionStatus
from application.ports.driven.db.connections.repository_port import ConnectionsRepositoryPort
from application.ports.driven.db.metadata.repository_port import MetadataRepositoryPort
from application.ports.driven.inspectors.database_inspector_port import DatabaseInspectorPort


class ConnectionsService:
    """Service for managing database connections."""

    def __init__(
        self,
        connections_repo: ConnectionsRepositoryPort,
        metadata_repo: MetadataRepositoryPort,
    ):
        self.connections_repo = connections_repo
        self.metadata_repo = metadata_repo

    async def create_connection(self, connection: Connection) -> Connection:
        """Create a new database connection."""
        # Validate connection name is unique
        existing = await self.connections_repo.get_by_name(connection.name)
        if existing:
            raise ValueError(f"Connection with name '{connection.name}' already exists")

        # Create connection
        saved_connection = await self.connections_repo.create(connection)
        return saved_connection

    async def get_all_connections(self) -> List[Connection]:
        """Get all database connections."""
        return await self.connections_repo.get_all()

    async def get_connection_by_id(self, connection_id: int) -> Optional[Connection]:
        """Get a connection by ID."""
        return await self.connections_repo.get_by_id(connection_id)

    async def get_connection_by_name(self, name: str) -> Optional[Connection]:
        """Get a connection by name."""
        return await self.connections_repo.get_by_name(name)

    async def update_connection(self, connection: Connection) -> Connection:
        """Update an existing connection."""
        if not connection.id:
            raise ValueError("Connection ID is required for update")

        # Validate connection exists
        existing = await self.connections_repo.get_by_id(connection.id)
        if not existing:
            raise ValueError(f"Connection with id {connection.id} not found")

        # If name changed, validate new name is unique
        if connection.name != existing.name:
            name_check = await self.connections_repo.get_by_name(connection.name)
            if name_check:
                raise ValueError(f"Connection with name '{connection.name}' already exists")

        return await self.connections_repo.update(connection)

    async def delete_connection(self, connection_id: int) -> bool:
        """Delete a connection and all its associated metadata."""
        # Delete all metadata first
        await self.metadata_repo.delete_metadata_by_connection(connection_id)

        # Delete connection
        return await self.connections_repo.delete(connection_id)

    async def test_connection(
        self, connection: Connection, inspector: DatabaseInspectorPort
    ) -> bool:
        """Test if a connection is valid."""
        return await inspector.test_connection(connection)

    async def update_connection_status(
        self, connection_id: int, status: ConnectionStatus
    ) -> Connection:
        """Update the status of a connection."""
        return await self.connections_repo.update_status(connection_id, status)

    async def update_last_introspection(self, connection_id: int) -> Connection:
        """Update the last introspection timestamp."""
        connection = await self.connections_repo.get_by_id(connection_id)
        if not connection:
            raise ValueError(f"Connection with id {connection_id} not found")

        connection.last_introspection = datetime.now()
        return await self.connections_repo.update(connection)
