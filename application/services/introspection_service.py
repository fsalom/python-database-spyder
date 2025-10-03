"""Database introspection service."""

from typing import List
from datetime import datetime

from domain.entities.connection import Connection
from domain.entities.discovered_table import DiscoveredTable, DiscoveredRelation
from application.ports.driven.db.metadata.repository_port import MetadataRepositoryPort
from application.ports.driven.inspectors.database_inspector_port import DatabaseInspectorPort
from infrastructure.inspectors.inspector_factory import InspectorFactory


class IntrospectionService:
    """Service for database introspection operations."""

    def __init__(self, metadata_repo: MetadataRepositoryPort):
        self.metadata_repo = metadata_repo

    async def introspect_database(
        self, connection: Connection
    ) -> tuple[List[DiscoveredTable], List[DiscoveredRelation]]:
        """
        Introspect a database connection and save the discovered metadata.

        Returns:
            Tuple of (tables, relations) that were discovered and saved.
        """
        # Create appropriate inspector for database type
        inspector: DatabaseInspectorPort = InspectorFactory.create_inspector(connection)

        # Test connection first
        is_connected = await inspector.test_connection(connection)
        if not is_connected:
            raise ConnectionError(f"Failed to connect to database '{connection.name}'")

        # Introspect tables and relations
        tables = await inspector.inspect_tables(connection)
        relations = await inspector.inspect_relations(connection)

        # Save discovered metadata
        saved_tables = await self.metadata_repo.save_tables(connection.id, tables)
        saved_relations = await self.metadata_repo.save_relations(
            connection.id, relations
        )

        return saved_tables, saved_relations

    async def get_tables_by_connection(
        self, connection_id: int
    ) -> List[DiscoveredTable]:
        """Get all discovered tables for a connection."""
        return await self.metadata_repo.get_tables_by_connection(connection_id)

    async def get_table_by_id(self, table_id: int) -> DiscoveredTable:
        """Get a specific discovered table by ID."""
        table = await self.metadata_repo.get_table_by_id(table_id)
        if not table:
            raise ValueError(f"Table with id {table_id} not found")
        return table

    async def get_relations_by_connection(
        self, connection_id: int
    ) -> List[DiscoveredRelation]:
        """Get all discovered relations for a connection."""
        return await self.metadata_repo.get_relations_by_connection(connection_id)

    async def refresh_metadata(
        self, connection: Connection
    ) -> tuple[List[DiscoveredTable], List[DiscoveredRelation]]:
        """
        Refresh metadata for a connection by re-introspecting the database.
        This replaces all existing metadata for the connection.
        """
        return await self.introspect_database(connection)

    async def delete_metadata(self, connection_id: int) -> bool:
        """Delete all metadata for a connection."""
        return await self.metadata_repo.delete_metadata_by_connection(connection_id)
