"""Connection repository port interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.connection import Connection, ConnectionUpdate


class ConnectionsRepositoryPort(ABC):
    """Port interface for Connection repository operations."""

    @abstractmethod
    async def create(self, connection: Connection) -> Connection:
        """Create a new connection."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> List[Connection]:
        """Get all connections."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, connection_id: int) -> Optional[Connection]:
        """Get connection by ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Connection]:
        """Get connection by name."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, connection: Connection) -> Connection:
        """Update an existing connection."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, connection_id: int) -> bool:
        """Delete a connection."""
        raise NotImplementedError
