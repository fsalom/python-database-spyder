"""Base database inspector with common functionality."""

from typing import Optional
from sqlalchemy import create_engine, inspect, MetaData, text
from sqlalchemy.engine import Engine
from application.ports.driven.inspectors.database_inspector_port import DatabaseInspectorPort
from domain.entities.connection import Connection


class BaseInspector(DatabaseInspectorPort):
    """Base inspector with common SQLAlchemy introspection functionality."""

    def _create_connection_url(self, connection: Connection) -> str:
        """
        Create SQLAlchemy connection URL from connection entity.

        Args:
            connection: Connection entity

        Returns:
            SQLAlchemy connection URL string
        """
        raise NotImplementedError("Subclasses must implement _create_connection_url")

    def _create_engine(self, connection: Connection) -> Engine:
        """
        Create SQLAlchemy engine for the connection.

        Args:
            connection: Connection entity

        Returns:
            SQLAlchemy Engine instance
        """
        url = self._create_connection_url(connection)
        return create_engine(url, echo=False, pool_pre_ping=True)

    async def test_connection(self, connection: Connection) -> bool:
        """
        Test if the connection to the database is successful.

        Args:
            connection: Database connection information

        Returns:
            True if connection successful, False otherwise
        """
        try:
            engine = self._create_engine(connection)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            engine.dispose()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    def _get_inspector(self, connection: Connection):
        """
        Get SQLAlchemy inspector for the connection.

        Args:
            connection: Connection entity

        Returns:
            SQLAlchemy Inspector instance
        """
        engine = self._create_engine(connection)
        return inspect(engine)

    def _map_sqlalchemy_type_to_string(self, col_type) -> str:
        """
        Map SQLAlchemy column type to string representation.

        Args:
            col_type: SQLAlchemy column type

        Returns:
            String representation of the type
        """
        type_str = str(col_type)
        # Remove length/precision info for cleaner representation
        if '(' in type_str:
            return type_str.split('(')[0]
        return type_str
