"""FastAPI router for SQL query execution."""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from config.database import get_db
from driven.db.connections.adapter import ConnectionsDBRepositoryAdapter
from application.services.connections_service import ConnectionsService
from application.services.query_execution_service import QueryExecutionService

router = APIRouter(prefix="/query", tags=["query"])


class ExecuteQueryRequest(BaseModel):
    """Request schema for executing SQL queries."""

    connection_id: int = Field(..., description="ID of the database connection")
    query: str = Field(..., description="SQL query to execute", min_length=1)
    limit: int = Field(default=100, description="Maximum number of rows to return", ge=1, le=1000)


class ExecuteQueryResponse(BaseModel):
    """Response schema for query execution results."""

    success: bool
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    execution_time_ms: float


def get_query_execution_service(
    db: AsyncSession = Depends(get_db),
) -> QueryExecutionService:
    """Dependency to get query execution service."""
    return QueryExecutionService(db)


def get_connections_service(
    db: AsyncSession = Depends(get_db),
) -> ConnectionsService:
    """Dependency to get connections service."""
    from driven.db.metadata.adapter import MetadataDBRepositoryAdapter
    connections_repo = ConnectionsDBRepositoryAdapter(db)
    metadata_repo = MetadataDBRepositoryAdapter(db)
    return ConnectionsService(connections_repo, metadata_repo)


@router.post("/execute", response_model=ExecuteQueryResponse)
async def execute_query(
    request: ExecuteQueryRequest,
    query_service: QueryExecutionService = Depends(get_query_execution_service),
    connections_service: ConnectionsService = Depends(get_connections_service),
):
    """
    Execute a SQL query on a specified database connection.
    Returns results with column names and rows.
    Limited to SELECT queries for safety.
    """
    # Get connection
    connection = await connections_service.get_connection_by_id(request.connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection with id {request.connection_id} not found",
        )

    # Validate query is a SELECT statement (basic security check)
    query_upper = request.query.strip().upper()
    if not query_upper.startswith("SELECT"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only SELECT queries are allowed for safety reasons",
        )

    try:
        result = await query_service.execute_query(
            connection=connection,
            query=request.query,
            limit=request.limit
        )

        return ExecuteQueryResponse(
            success=True,
            columns=result["columns"],
            rows=result["rows"],
            row_count=result["row_count"],
            execution_time_ms=result["execution_time_ms"]
        )
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}",
        )
