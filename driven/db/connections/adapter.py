"""Connection repository adapter using SQLAlchemy async."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.ports.driven.db.connections.repository_port import ConnectionsRepositoryPort
from domain.entities.connection import Connection
from driven.db.connections.mapper import ConnectionDBOMapper
from driven.db.connections.models import ConnectionDBO


class ConnectionsDBRepositoryAdapter(ConnectionsRepositoryPort):
    """Implementation of Connection repository using SQLAlchemy async methods."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = ConnectionDBOMapper()

    async def create(self, connection: Connection) -> Connection:
        """Create a new connection."""
        dbo = await self.mapper.entity_to_dbo(connection)
        self.session.add(dbo)
        await self.session.flush()
        await self.session.refresh(dbo)

        return await self.mapper.dbo_to_entity(dbo)

    async def get_all(self) -> List[Connection]:
        """Get all connections."""
        stmt = select(ConnectionDBO).order_by(ConnectionDBO.created_at.desc())
        result = await self.session.execute(stmt)
        dbos = result.scalars().all()

        return [await self.mapper.dbo_to_entity(dbo) for dbo in dbos]

    async def get_by_id(self, connection_id: int) -> Optional[Connection]:
        """Get connection by ID."""
        stmt = select(ConnectionDBO).where(ConnectionDBO.id == connection_id)
        result = await self.session.execute(stmt)
        dbo = result.scalar_one_or_none()

        if dbo is None:
            return None

        return await self.mapper.dbo_to_entity(dbo)

    async def get_by_name(self, name: str) -> Optional[Connection]:
        """Get connection by name."""
        stmt = select(ConnectionDBO).where(ConnectionDBO.name == name)
        result = await self.session.execute(stmt)
        dbo = result.scalar_one_or_none()

        if dbo is None:
            return None

        return await self.mapper.dbo_to_entity(dbo)

    async def update(self, connection: Connection) -> Connection:
        """Update an existing connection."""
        stmt = select(ConnectionDBO).where(ConnectionDBO.id == connection.id)
        result = await self.session.execute(stmt)
        dbo = result.scalar_one_or_none()

        if dbo is None:
            raise ValueError(f"Connection with id {connection.id} not found")

        # Update fields
        dbo.name = connection.name
        dbo.database_type = connection.database_type.value if hasattr(connection.database_type, 'value') else connection.database_type
        dbo.host = connection.host
        dbo.port = connection.port
        dbo.database = connection.database
        dbo.username = connection.username
        dbo.password = connection.password  # TODO: Encrypt
        dbo.db_schema = connection.db_schema
        dbo.ssl_enabled = connection.ssl_enabled
        dbo.status = connection.status.value if hasattr(connection.status, 'value') else connection.status
        dbo.last_introspection = connection.last_introspection

        await self.session.flush()
        await self.session.refresh(dbo)

        return await self.mapper.dbo_to_entity(dbo)

    async def delete(self, connection_id: int) -> bool:
        """Delete a connection."""
        stmt = select(ConnectionDBO).where(ConnectionDBO.id == connection_id)
        result = await self.session.execute(stmt)
        dbo = result.scalar_one_or_none()

        if dbo is None:
            return False

        await self.session.delete(dbo)
        await self.session.flush()
        return True
