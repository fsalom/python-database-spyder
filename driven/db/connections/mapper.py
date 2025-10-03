"""Mapper between Connection entities and database objects."""

from domain.entities.connection import Connection
from driven.db.connections.models import ConnectionDBO


class ConnectionDBOMapper:
    """Maps between Connection domain entities and ConnectionDBO database objects."""

    async def entity_to_dbo(self, entity: Connection) -> ConnectionDBO:
        """Convert Connection entity to ConnectionDBO."""
        # Handle both enum and string values
        db_type = entity.database_type.value if hasattr(entity.database_type, 'value') else entity.database_type
        status = entity.status.value if hasattr(entity.status, 'value') else entity.status

        dbo = ConnectionDBO(
            name=entity.name,
            database_type=db_type,
            host=entity.host,
            port=entity.port,
            database=entity.database,
            username=entity.username,
            password=entity.password,  # TODO: Encrypt before storing
            db_schema=entity.db_schema,
            ssl_enabled=entity.ssl_enabled,
            status=status,
            last_introspection=entity.last_introspection,
        )

        if hasattr(entity, 'id') and entity.id is not None:
            dbo.id = entity.id

        return dbo

    async def dbo_to_entity(self, dbo: ConnectionDBO) -> Connection:
        """Convert ConnectionDBO to Connection entity."""
        return Connection(
            id=dbo.id,
            name=dbo.name,
            database_type=dbo.database_type,
            host=dbo.host,
            port=dbo.port,
            database=dbo.database,
            username=dbo.username,
            password=dbo.password,  # TODO: Decrypt after reading
            db_schema=dbo.db_schema,
            ssl_enabled=dbo.ssl_enabled,
            status=dbo.status,
            last_introspection=dbo.last_introspection,
            created_at=dbo.created_at,
            updated_at=dbo.updated_at,
        )
