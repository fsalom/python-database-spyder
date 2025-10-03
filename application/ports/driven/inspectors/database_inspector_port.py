"""Database inspector port interface."""

from abc import ABC, abstractmethod
from typing import List
from domain.entities.discovered_table import (
    DiscoveredTable,
    DiscoveredColumn,
    DiscoveredRelation,
)
from domain.entities.connection import Connection


class DatabaseInspectorPort(ABC):
    """Port interface for database introspection."""

    @abstractmethod
    async def inspect_tables(self, connection: Connection) -> List[DiscoveredTable]:
        """
        Inspect all tables in the database.

        Args:
            connection: Database connection information

        Returns:
            List of discovered tables with their columns
        """
        raise NotImplementedError

    @abstractmethod
    async def inspect_table(
        self, connection: Connection, table_name: str, schema_name: str = None
    ) -> DiscoveredTable:
        """
        Inspect a specific table.

        Args:
            connection: Database connection information
            table_name: Name of the table to inspect
            schema_name: Schema name (optional)

        Returns:
            Discovered table with columns
        """
        raise NotImplementedError

    @abstractmethod
    async def inspect_relations(
        self, connection: Connection
    ) -> List[DiscoveredRelation]:
        """
        Inspect foreign key relationships in the database.

        Args:
            connection: Database connection information

        Returns:
            List of discovered relationships
        """
        raise NotImplementedError

    @abstractmethod
    async def test_connection(self, connection: Connection) -> bool:
        """
        Test if the connection to the database is successful.

        Args:
            connection: Database connection information

        Returns:
            True if connection successful, False otherwise
        """
        raise NotImplementedError
