"""Pydantic schemas for Introspection API."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class DiscoveredColumnResponse(BaseModel):
    """Schema for discovered column response."""

    id: int
    table_id: int
    column_name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool
    is_foreign_key: bool
    foreign_key_table: Optional[str] = None
    foreign_key_column: Optional[str] = None
    default_value: Optional[str] = None
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    ordinal_position: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DiscoveredTableResponse(BaseModel):
    """Schema for discovered table response."""

    id: int
    connection_id: int
    table_name: str
    schema_name: Optional[str] = None
    table_type: Optional[str] = None
    row_count: Optional[int] = None
    comment: Optional[str] = None
    created_at: datetime
    columns: List[DiscoveredColumnResponse] = []
    primary_key_columns: Optional[List[str]] = None

    model_config = {"from_attributes": True}

    @property
    def _primary_key_columns(self) -> List[str]:
        """Compute primary key columns from the columns list."""
        return [col.column_name for col in self.columns if col.is_primary_key]

    def model_post_init(self, __context):
        """Set primary_key_columns after initialization."""
        if self.primary_key_columns is None:
            self.primary_key_columns = self._primary_key_columns


class DiscoveredRelationResponse(BaseModel):
    """Schema for discovered relation response."""

    id: int
    from_table_id: int
    to_table_id: int
    from_column_id: int
    to_column_id: int
    relation_type: str
    constraint_name: Optional[str] = None
    on_delete: str
    on_update: str
    created_at: datetime

    model_config = {"from_attributes": True}


class IntrospectionRequest(BaseModel):
    """Schema for introspection request."""

    connection_id: int


class IntrospectionResponse(BaseModel):
    """Schema for introspection response."""

    success: bool
    message: str
    tables_count: int
    relations_count: int
