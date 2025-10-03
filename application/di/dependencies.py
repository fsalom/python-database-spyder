"""FastAPI dependencies for dependency injection."""

from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from application.services.users_service import UsersService
from driven.db.users.adapter import UsersDBRepositoryAdapter


async def get_users_service(
    db: AsyncSession = Depends(get_db)
) -> AsyncGenerator[UsersService, None]:
    """
    FastAPI dependency for users service.

    Injects database session and creates service with repository.
    """
    users_repository = UsersDBRepositoryAdapter(db)
    service = UsersService(users_repository)
    yield service


# You can add more service dependencies here as needed:
# async def get_connections_service(db: AsyncSession = Depends(get_db)) -> ConnectionsService:
#     connections_repository = ConnectionsDBRepositoryAdapter(db)
#     return ConnectionsService(connections_repository)
