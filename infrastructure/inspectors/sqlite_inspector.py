"""SQLite database inspector."""

from typing import List
from infrastructure.inspectors.base_inspector import BaseInspector
from domain.entities.connection import Connection
from domain.entities.discovered_table import (
    DiscoveredTable,
    DiscoveredColumn,
    DiscoveredRelation,
)


class SQLiteInspector(BaseInspector):
    """SQLite-specific database inspector."""

    def _create_connection_url(self, connection: Connection) -> str:
        """Create SQLite connection URL."""
        # For SQLite, the 'database' field contains the file path
        return f"sqlite:///{connection.database}"

    async def inspect_tables(self, connection: Connection) -> List[DiscoveredTable]:
        """Inspect all tables in SQLite database."""
        inspector = self._get_inspector(connection)

        tables = []
        table_names = inspector.get_table_names()

        for table_name in table_names:
            discovered_table = await self.inspect_table(connection, table_name)
            tables.append(discovered_table)

        return tables

    async def inspect_table(
        self, connection: Connection, table_name: str, schema_name: str = None
    ) -> DiscoveredTable:
        """Inspect a specific SQLite table."""
        inspector = self._get_inspector(connection)

        # SQLite doesn't have table comments in standard way
        comment = None

        # Get columns
        columns_info = inspector.get_columns(table_name)
        pk_constraint = inspector.get_pk_constraint(table_name)
        pk_columns = pk_constraint.get("constrained_columns", []) if pk_constraint else []

        fk_constraints = inspector.get_foreign_keys(table_name)
        fk_columns = [fk["constrained_columns"][0] for fk in fk_constraints if fk.get("constrained_columns")]

        columns = []
        for idx, col_info in enumerate(columns_info):
            col_name = col_info["name"]
            col_type = col_info["type"]

            column = DiscoveredColumn(
                table_id=0,
                column_name=col_name,
                data_type=self._map_sqlalchemy_type_to_string(col_type),
                is_nullable=col_info.get("nullable", True),
                is_primary_key=col_name in pk_columns,
                is_foreign_key=col_name in fk_columns,
                default_value=str(col_info.get("default")) if col_info.get("default") else None,
                max_length=getattr(col_type, "length", None),
                precision=getattr(col_type, "precision", None),
                scale=getattr(col_type, "scale", None),
                ordinal_position=idx + 1,
            )
            columns.append(column)

        discovered_table = DiscoveredTable(
            connection_id=0,
            table_name=table_name,
            schema_name="main",  # SQLite default schema
            table_type="TABLE",
            comment=comment,
            columns=columns,
        )

        return discovered_table

    async def inspect_relations(
        self, connection: Connection
    ) -> List[DiscoveredRelation]:
        """Inspect foreign key relationships in SQLite database."""
        inspector = self._get_inspector(connection)

        relations = []
        table_names = inspector.get_table_names()

        for table_name in table_names:
            fk_constraints = inspector.get_foreign_keys(table_name)

            for fk in fk_constraints:
                if not fk.get("constrained_columns") or not fk.get("referred_columns"):
                    continue

                relation = DiscoveredRelation(
                    from_table_id=0,
                    to_table_id=0,
                    from_column_id=0,
                    to_column_id=0,
                    relation_type="many_to_one",
                    constraint_name=fk.get("name"),
                    on_delete=fk.get("options", {}).get("ondelete", "NO ACTION"),
                    on_update=fk.get("options", {}).get("onupdate", "NO ACTION"),
                    from_table_name=table_name,
                    to_table_name=fk["referred_table"],
                    from_column_name=fk["constrained_columns"][0],
                    to_column_name=fk["referred_columns"][0],
                )
                relations.append(relation)

        return relations
