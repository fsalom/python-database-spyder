"""Query execution service."""

import time
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text

from domain.entities.connection import Connection


class QueryExecutionService:
    """Service for executing SQL queries on database connections."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _build_connection_url(self, connection: Connection) -> str:
        """Build SQLAlchemy connection URL from connection entity."""
        db_type = connection.database_type.lower()

        # Map database types to SQLAlchemy drivers
        driver_map = {
            "postgresql": "postgresql+asyncpg",
            "mysql": "mysql+aiomysql",
            "sqlite": "sqlite+aiosqlite",
        }

        driver = driver_map.get(db_type)
        if not driver:
            raise ValueError(f"Unsupported database type: {db_type}")

        if db_type == "sqlite":
            return f"{driver}:///{connection.database}"

        # Build URL with credentials
        url = f"{driver}://{connection.username}:{connection.password}@{connection.host}:{connection.port}/{connection.database}"
        return url

    async def execute_query(
        self,
        connection: Connection,
        query: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Execute a SQL query on the specified connection.

        Args:
            connection: Database connection entity
            query: SQL query to execute
            limit: Maximum number of rows to return

        Returns:
            Dictionary with columns, rows, row_count, and execution_time_ms
        """
        connection_url = self._build_connection_url(connection)

        # Create temporary engine for this query
        engine = create_async_engine(
            connection_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

        try:
            start_time = time.time()

            async with engine.connect() as conn:
                # Add LIMIT to query if not present
                query_with_limit = query.strip()
                if not query_with_limit.upper().endswith(';'):
                    query_with_limit += ';'

                # Remove trailing semicolon for LIMIT addition
                query_with_limit = query_with_limit[:-1].strip()

                # Add LIMIT if not already present
                if 'LIMIT' not in query_with_limit.upper():
                    query_with_limit = f"{query_with_limit} LIMIT {limit}"

                # Execute query
                result = await conn.execute(text(query_with_limit))

                # Fetch all rows
                rows_data = result.fetchall()

                # Get column names
                columns = list(result.keys()) if result.keys() else []

                # Convert rows to list of dicts
                rows = []
                for row in rows_data:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        # Convert non-serializable types to strings
                        if value is not None and not isinstance(value, (str, int, float, bool)):
                            value = str(value)
                        row_dict[col] = value
                    rows.append(row_dict)

                execution_time = (time.time() - start_time) * 1000  # Convert to ms

                return {
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows),
                    "execution_time_ms": round(execution_time, 2)
                }

        except Exception as e:
            raise Exception(f"Query execution error: {str(e)}")
        finally:
            await engine.dispose()
