"""Factory for creating database inspectors."""

from application.ports.driven.inspectors.database_inspector_port import DatabaseInspectorPort
from domain.entities.connection import Connection, DatabaseType
from infrastructure.inspectors.postgres_inspector import PostgreSQLInspector
from infrastructure.inspectors.mysql_inspector import MySQLInspector
from infrastructure.inspectors.sqlite_inspector import SQLiteInspector


class InspectorFactory:
    """Factory for creating database-specific inspectors."""

    @staticmethod
    def create_inspector(connection: Connection) -> DatabaseInspectorPort:
        """
        Create appropriate inspector based on database type.

        Args:
            connection: Connection entity with database type

        Returns:
            Database-specific inspector instance

        Raises:
            ValueError: If database type is not supported
        """
        if connection.database_type == DatabaseType.POSTGRESQL:
            return PostgreSQLInspector()
        elif connection.database_type == DatabaseType.MYSQL:
            return MySQLInspector()
        elif connection.database_type == DatabaseType.SQLITE:
            return SQLiteInspector()
        else:
            raise ValueError(
                f"Unsupported database type: {connection.database_type}. "
                f"Supported types: PostgreSQL, MySQL, SQLite"
            )

    @staticmethod
    def get_supported_databases() -> list[str]:
        """Get list of supported database types."""
        return [
            DatabaseType.POSTGRESQL,
            DatabaseType.MYSQL,
            DatabaseType.SQLITE,
        ]
