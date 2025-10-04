"""User repository adapter using SQLAlchemy async."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.ports.driven.db.users.repository_port import UsersRepositoryPort
from domain.entities.user import User
from driven.db.users.models import UserDBO
from driven.db.users.mapper import UserDBOMapper


class UsersDBRepositoryAdapter(UsersRepositoryPort):
    """Implementation of User repository using SQLAlchemy async methods."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = UserDBOMapper()

    async def create(self, user: User) -> User:
        """Create a new user."""
        dbo = await self.mapper.entity_to_dbo(user)
        self.session.add(dbo)
        await self.session.flush()
        await self.session.refresh(dbo)

        return await self.mapper.dbo_to_entity(dbo)

    async def get_all(self) -> List[User]:
        """Get all users."""
        stmt = select(UserDBO).order_by(UserDBO.created_at.desc())
        result = await self.session.execute(stmt)
        dbos = result.scalars().all()

        return [await self.mapper.dbo_to_entity(dbo) for dbo in dbos]

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        stmt = select(UserDBO).where(UserDBO.id == user_id)
        result = await self.session.execute(stmt)
        dbo = result.scalar_one_or_none()

        if dbo is None:
            return None

        return await self.mapper.dbo_to_entity(dbo)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        stmt = select(UserDBO).where(UserDBO.email == email)
        result = await self.session.execute(stmt)
        dbo = result.scalar_one_or_none()

        if dbo is None:
            return None

        return await self.mapper.dbo_to_entity(dbo)

    async def update(self, user: User) -> User:
        """Update an existing user."""
        stmt = select(UserDBO).where(UserDBO.id == user.id)
        result = await self.session.execute(stmt)
        dbo = result.scalar_one_or_none()

        if dbo is None:
            raise ValueError(f"User with id {user.id} not found")

        # Update fields
        dbo.email = user.email
        dbo.full_name = user.full_name
        dbo.hashed_password = user.hashed_password
        dbo.is_active = user.is_active
        dbo.is_superuser = user.is_superuser

        await self.session.flush()
        await self.session.refresh(dbo)

        return await self.mapper.dbo_to_entity(dbo)

    async def delete(self, user_id: int) -> bool:
        """Delete a user."""
        stmt = select(UserDBO).where(UserDBO.id == user_id)
        result = await self.session.execute(stmt)
        dbo = result.scalar_one_or_none()

        if dbo is None:
            return False

        await self.session.delete(dbo)
        await self.session.flush()
        return True
