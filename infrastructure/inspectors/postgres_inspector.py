"""PostgreSQL database inspector."""

from typing import List, Optional
from infrastructure.inspectors.base_inspector import BaseInspector
from domain.entities.connection import Connection
from domain.entities.discovered_table import (
    DiscoveredTable,
    DiscoveredColumn,
    DiscoveredRelation,
)


class PostgreSQLInspector(BaseInspector):
    """PostgreSQL-specific database inspector."""

    def _create_connection_url(self, connection: Connection) -> str:
        """Create PostgreSQL connection URL."""
        # Use asyncpg for async, psycopg2 for sync introspection
        return (
            f"postgresql://{connection.username}:{connection.password}"
            f"@{connection.host}:{connection.port}/{connection.database}"
        )

    async def inspect_tables(self, connection: Connection) -> List[DiscoveredTable]:
        """
        Inspect all tables in PostgreSQL database.

        Args:
            connection: Database connection information

        Returns:
            List of discovered tables with columns
        """
        inspector = self._get_inspector(connection)
        schema = connection.db_schema or "public"

        tables = []
        table_names = inspector.get_table_names(schema=schema)

        for table_name in table_names:
            discovered_table = await self.inspect_table(connection, table_name, schema)
            tables.append(discovered_table)

        return tables

    async def inspect_table(
        self, connection: Connection, table_name: str, schema_name: str = None
    ) -> DiscoveredTable:
        """
        Inspect a specific PostgreSQL table.

        Args:
            connection: Database connection information
            table_name: Name of the table
            schema_name: Schema name (defaults to 'public')

        Returns:
            Discovered table with columns
        """
        inspector = self._get_inspector(connection)
        schema = schema_name or connection.db_schema or "public"

        # Get table comment
        comment = None
        try:
            comment_info = inspector.get_table_comment(table_name, schema=schema)
            comment = comment_info.get("text") if comment_info else None
        except:
            pass

        # Get columns
        columns_info = inspector.get_columns(table_name, schema=schema)
        pk_constraint = inspector.get_pk_constraint(table_name, schema=schema)
        pk_columns = pk_constraint.get("constrained_columns", []) if pk_constraint else []

        fk_constraints = inspector.get_foreign_keys(table_name, schema=schema)
        fk_columns = [fk["constrained_columns"][0] for fk in fk_constraints if fk.get("constrained_columns")]

        # Create a mapping of column -> (referred_table, referred_column)
        fk_mapping = {}
        for fk in fk_constraints:
            if fk.get("constrained_columns") and fk.get("referred_table") and fk.get("referred_columns"):
                col_name = fk["constrained_columns"][0]
                fk_mapping[col_name] = {
                    "table": fk["referred_table"],
                    "column": fk["referred_columns"][0] if fk["referred_columns"] else None
                }

        columns = []
        for idx, col_info in enumerate(columns_info):
            col_name = col_info["name"]
            col_type = col_info["type"]

            fk_info = fk_mapping.get(col_name)

            fk_table = fk_info.get("table") if fk_info else None
            fk_column = fk_info.get("column") if fk_info else None

            column = DiscoveredColumn(
                table_id=0,  # Will be set when saving
                column_name=col_name,
                data_type=self._map_sqlalchemy_type_to_string(col_type),
                is_nullable=col_info.get("nullable", True),
                is_primary_key=col_name in pk_columns,
                is_foreign_key=col_name in fk_columns,
                foreign_key_table=fk_table,
                foreign_key_column=fk_column,
                default_value=str(col_info.get("default")) if col_info.get("default") else None,
                max_length=getattr(col_type, "length", None),
                precision=getattr(col_type, "precision", None),
                scale=getattr(col_type, "scale", None),
                ordinal_position=idx + 1,
            )
            columns.append(column)

        # Create table entity
        discovered_table = DiscoveredTable(
            connection_id=0,  # Will be set when saving
            table_name=table_name,
            schema_name=schema,
            table_type="TABLE",
            comment=comment,
            columns=columns,
        )

        return discovered_table

    async def inspect_relations(
        self, connection: Connection
    ) -> List[DiscoveredRelation]:
        """
        Inspect foreign key relationships in PostgreSQL database.

        Args:
            connection: Database connection information

        Returns:
            List of discovered relationships
        """
        inspector = self._get_inspector(connection)
        schema = connection.db_schema or "public"

        relations = []
        table_names = inspector.get_table_names(schema=schema)

        for table_name in table_names:
            fk_constraints = inspector.get_foreign_keys(table_name, schema=schema)

            for fk in fk_constraints:
                if not fk.get("constrained_columns") or not fk.get("referred_columns"):
                    continue

                relation = DiscoveredRelation(
                    from_table_id=0,  # Will be resolved when saving
                    to_table_id=0,    # Will be resolved when saving
                    from_column_id=0,  # Will be resolved when saving
                    to_column_id=0,    # Will be resolved when saving
                    relation_type="many_to_one",  # Default, can be analyzed further
                    constraint_name=fk.get("name"),
                    on_delete=fk.get("options", {}).get("ondelete", "NO ACTION"),
                    on_update=fk.get("options", {}).get("onupdate", "NO ACTION"),
                    # Temporary storage for resolution
                    from_table_name=table_name,
                    to_table_name=fk["referred_table"],
                    from_column_name=fk["constrained_columns"][0],
                    to_column_name=fk["referred_columns"][0],
                )
                relations.append(relation)

        return relations
