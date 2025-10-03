"""Metadata repository adapter using SQLAlchemy async."""

from typing import List, Optional, Dict
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from application.ports.driven.db.metadata.repository_port import MetadataRepositoryPort
from domain.entities.discovered_table import (
    DiscoveredTable,
    DiscoveredColumn,
    DiscoveredRelation,
)
from driven.db.metadata.models import (
    DiscoveredTableDBO,
    DiscoveredColumnDBO,
    DiscoveredRelationDBO,
)


class MetadataDBRepositoryAdapter(MetadataRepositoryPort):
    """Implementation of Metadata repository using SQLAlchemy async methods."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_tables(
        self, connection_id: int, tables: List[DiscoveredTable]
    ) -> List[DiscoveredTable]:
        """Save discovered tables for a connection. Replaces existing tables."""

        # Delete existing tables for this connection (cascade will delete columns/relations)
        await self.session.execute(
            delete(DiscoveredTableDBO).where(
                DiscoveredTableDBO.connection_id == connection_id
            )
        )
        await self.session.flush()

        # Create new tables
        saved_tables = []
        for table in tables:
            table_dbo = DiscoveredTableDBO(
                connection_id=connection_id,
                table_name=table.table_name,
                schema_name=table.schema_name,
                table_type=table.table_type,
                row_count=table.row_count,
                comment=table.comment,
            )
            self.session.add(table_dbo)
            await self.session.flush()  # Get ID
            await self.session.refresh(table_dbo)

            # Create columns
            for column in table.columns:
                column_dbo = DiscoveredColumnDBO(
                    table_id=table_dbo.id,
                    column_name=column.column_name,
                    data_type=column.data_type,
                    is_nullable=column.is_nullable,
                    is_primary_key=column.is_primary_key,
                    is_foreign_key=column.is_foreign_key,
                    default_value=column.default_value,
                    max_length=column.max_length,
                    precision=column.precision,
                    scale=column.scale,
                    ordinal_position=column.ordinal_position,
                )
                self.session.add(column_dbo)

            await self.session.flush()

        # Reload all tables with their columns (eager loading)
        stmt = (
            select(DiscoveredTableDBO)
            .options(selectinload(DiscoveredTableDBO.columns))
            .where(DiscoveredTableDBO.connection_id == connection_id)
        )
        result = await self.session.execute(stmt)
        table_dbos = result.scalars().all()

        # Convert to entities
        saved_tables = [await self._dbo_to_entity(table_dbo) for table_dbo in table_dbos]

        return saved_tables

    async def save_relations(
        self, connection_id: int, relations: List[DiscoveredRelation]
    ) -> List[DiscoveredRelation]:
        """Save discovered relations for a connection."""

        # Delete existing relations for this connection
        stmt = select(DiscoveredTableDBO.id).where(
            DiscoveredTableDBO.connection_id == connection_id
        )
        result = await self.session.execute(stmt)
        table_ids = [row[0] for row in result.all()]

        if table_ids:
            await self.session.execute(
                delete(DiscoveredRelationDBO).where(
                    DiscoveredRelationDBO.from_table_id.in_(table_ids)
                )
            )
            await self.session.flush()

        # Build lookup maps
        table_map, column_map = await self._build_lookup_maps(connection_id)

        # Create new relations
        saved_relations = []
        for relation in relations:
            # Resolve IDs from names
            from_table_id = table_map.get(relation.from_table_name)
            to_table_id = table_map.get(relation.to_table_name)

            if not from_table_id or not to_table_id:
                print(f"Warning: Could not resolve table names for relation: {relation.from_table_name} -> {relation.to_table_name}")
                continue

            from_column_key = (from_table_id, relation.from_column_name)
            to_column_key = (to_table_id, relation.to_column_name)

            from_column_id = column_map.get(from_column_key)
            to_column_id = column_map.get(to_column_key)

            if not from_column_id or not to_column_id:
                print(f"Warning: Could not resolve column names for relation")
                continue

            relation_dbo = DiscoveredRelationDBO(
                from_table_id=from_table_id,
                to_table_id=to_table_id,
                from_column_id=from_column_id,
                to_column_id=to_column_id,
                relation_type=relation.relation_type,
                constraint_name=relation.constraint_name,
                on_delete=relation.on_delete,
                on_update=relation.on_update,
            )
            self.session.add(relation_dbo)

        await self.session.flush()
        return relations  # Simplified, return input

    async def get_tables_by_connection(
        self, connection_id: int
    ) -> List[DiscoveredTable]:
        """Get all tables for a connection."""
        stmt = (
            select(DiscoveredTableDBO)
            .options(selectinload(DiscoveredTableDBO.columns))
            .where(DiscoveredTableDBO.connection_id == connection_id)
            .order_by(DiscoveredTableDBO.table_name)
        )
        result = await self.session.execute(stmt)
        dbos = result.scalars().all()

        return [await self._dbo_to_entity(dbo) for dbo in dbos]

    async def get_table_by_id(self, table_id: int) -> Optional[DiscoveredTable]:
        """Get a specific table by ID."""
        stmt = (
            select(DiscoveredTableDBO)
            .options(selectinload(DiscoveredTableDBO.columns))
            .where(DiscoveredTableDBO.id == table_id)
        )
        result = await self.session.execute(stmt)
        dbo = result.scalar_one_or_none()

        if dbo is None:
            return None

        return await self._dbo_to_entity(dbo)

    async def get_relations_by_connection(
        self, connection_id: int
    ) -> List[DiscoveredRelation]:
        """Get all relations for a connection."""
        # Get all table IDs for this connection
        stmt = select(DiscoveredTableDBO.id).where(
            DiscoveredTableDBO.connection_id == connection_id
        )
        result = await self.session.execute(stmt)
        table_ids = [row[0] for row in result.all()]

        if not table_ids:
            return []

        # Get relations
        stmt = select(DiscoveredRelationDBO).where(
            DiscoveredRelationDBO.from_table_id.in_(table_ids)
        )
        result = await self.session.execute(stmt)
        dbos = result.scalars().all()

        return [self._relation_dbo_to_entity(dbo) for dbo in dbos]

    async def delete_metadata_by_connection(self, connection_id: int) -> bool:
        """Delete all metadata for a connection."""
        await self.session.execute(
            delete(DiscoveredTableDBO).where(
                DiscoveredTableDBO.connection_id == connection_id
            )
        )
        await self.session.flush()
        return True

    async def _build_lookup_maps(self, connection_id: int) -> tuple[Dict, Dict]:
        """Build lookup maps for resolving table/column names to IDs."""
        stmt = (
            select(DiscoveredTableDBO)
            .options(selectinload(DiscoveredTableDBO.columns))
            .where(DiscoveredTableDBO.connection_id == connection_id)
        )
        result = await self.session.execute(stmt)
        tables = result.scalars().all()

        table_map = {table.table_name: table.id for table in tables}
        column_map = {
            (table.id, col.column_name): col.id
            for table in tables
            for col in table.columns
        }

        return table_map, column_map

    async def _dbo_to_entity(self, dbo: DiscoveredTableDBO) -> DiscoveredTable:
        """Convert DiscoveredTableDBO to DiscoveredTable entity."""
        columns = [
            DiscoveredColumn(
                id=col.id,
                table_id=col.table_id,
                column_name=col.column_name,
                data_type=col.data_type,
                is_nullable=col.is_nullable,
                is_primary_key=col.is_primary_key,
                is_foreign_key=col.is_foreign_key,
                default_value=col.default_value,
                max_length=col.max_length,
                precision=col.precision,
                scale=col.scale,
                ordinal_position=col.ordinal_position,
                created_at=col.created_at,
            )
            for col in dbo.columns
        ]

        return DiscoveredTable(
            id=dbo.id,
            connection_id=dbo.connection_id,
            table_name=dbo.table_name,
            schema_name=dbo.schema_name,
            table_type=dbo.table_type,
            row_count=dbo.row_count,
            comment=dbo.comment,
            created_at=dbo.created_at,
            columns=columns,
        )

    def _relation_dbo_to_entity(self, dbo: DiscoveredRelationDBO) -> DiscoveredRelation:
        """Convert DiscoveredRelationDBO to DiscoveredRelation entity."""
        return DiscoveredRelation(
            id=dbo.id,
            from_table_id=dbo.from_table_id,
            to_table_id=dbo.to_table_id,
            from_column_id=dbo.from_column_id,
            to_column_id=dbo.to_column_id,
            relation_type=dbo.relation_type,
            constraint_name=dbo.constraint_name,
            on_delete=dbo.on_delete,
            on_update=dbo.on_update,
            created_at=dbo.created_at,
        )
