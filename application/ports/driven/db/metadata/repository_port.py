"""Metadata repository port interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.discovered_table import (
    DiscoveredTable,
    DiscoveredColumn,
    DiscoveredRelation,
)


class MetadataRepositoryPort(ABC):
    """Port interface for Metadata repository operations."""

    @abstractmethod
    async def save_tables(
        self, connection_id: int, tables: List[DiscoveredTable]
    ) -> List[DiscoveredTable]:
        """
        Save discovered tables for a connection.
        Replaces existing tables for this connection.
        """
        raise NotImplementedError

    @abstractmethod
    async def save_relations(
        self, connection_id: int, relations: List[DiscoveredRelation]
    ) -> List[DiscoveredRelation]:
        """
        Save discovered relations for a connection.
        Replaces existing relations for this connection.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_tables_by_connection(
        self, connection_id: int
    ) -> List[DiscoveredTable]:
        """Get all tables for a connection."""
        raise NotImplementedError

    @abstractmethod
    async def get_table_by_id(self, table_id: int) -> Optional[DiscoveredTable]:
        """Get a specific table by ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_relations_by_connection(
        self, connection_id: int
    ) -> List[DiscoveredRelation]:
        """Get all relations for a connection."""
        raise NotImplementedError

    @abstractmethod
    async def delete_metadata_by_connection(self, connection_id: int) -> bool:
        """Delete all metadata for a connection."""
        raise NotImplementedError
