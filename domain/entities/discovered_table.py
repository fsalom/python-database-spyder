"""Discovered table domain entities."""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class DiscoveredColumn(BaseModel):
    """Discovered column domain entity."""

    id: Optional[int] = None
    table_id: int
    column_name: str
    data_type: str
    is_nullable: bool = True
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_table: Optional[str] = None
    foreign_key_column: Optional[str] = None
    default_value: Optional[str] = None
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    ordinal_position: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DiscoveredTable(BaseModel):
    """Discovered table domain entity."""

    id: Optional[int] = None
    connection_id: int
    table_name: str
    schema_name: Optional[str] = None
    table_type: str = Field(default="TABLE", description="TABLE, VIEW, etc.")
    row_count: Optional[int] = None
    comment: Optional[str] = None
    created_at: Optional[datetime] = None
    columns: List[DiscoveredColumn] = []

    class Config:
        from_attributes = True


class RelationType(str):
    """Types of relationships between tables."""

    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"


class DiscoveredRelation(BaseModel):
    """Discovered relationship domain entity."""

    id: Optional[int] = None
    from_table_id: int
    to_table_id: int
    from_column_id: int
    to_column_id: int
    relation_type: str = Field(default=RelationType.MANY_TO_ONE)
    constraint_name: Optional[str] = None
    on_delete: Optional[str] = Field(default="NO ACTION", description="CASCADE, SET NULL, etc.")
    on_update: Optional[str] = Field(default="NO ACTION")
    created_at: Optional[datetime] = None

    # Populated fields (not in DB, loaded via joins)
    from_table_name: Optional[str] = None
    to_table_name: Optional[str] = None
    from_column_name: Optional[str] = None
    to_column_name: Optional[str] = None

    class Config:
        from_attributes = True
