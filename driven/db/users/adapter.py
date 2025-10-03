"""User repository adapter using SQLAlchemy async."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from application.ports.driven.db.users.repository_port import UsersRepositoryPort
from domain.entities.users import User
from driven.db.users.mapper import UserDBOMapper
from driven.db.users.models import UserDBO, DepartmentDBO


class UsersDBRepositoryAdapter(UsersRepositoryPort):
    """Implementation of User repository using SQLAlchemy async methods."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = UserDBOMapper()

    async def create(self, user: User) -> User:
        """Create a new user."""
        dbo = await self.mapper.entity_to_dbo(user)

        # Handle departments if present
        if user.departments:
            department_names = [dept.name for dept in user.departments]
            departments = []

            for dept_name in department_names:
                # Check if department exists
                stmt = select(DepartmentDBO).where(DepartmentDBO.name == dept_name)
                result = await self.session.execute(stmt)
                dept = result.scalar_one_or_none()

                if not dept:
                    # Create new department
                    dept = DepartmentDBO(name=dept_name)
                    self.session.add(dept)
                    await self.session.flush()  # Get the ID

                departments.append(dept)

            dbo.departments = departments

        self.session.add(dbo)
        await self.session.flush()
        await self.session.refresh(dbo, ["departments"])

        return await self.mapper.dbo_to_entity(dbo)

    async def get_all(self) -> List[User]:
        """Get all users."""
        stmt = select(UserDBO).options(selectinload(UserDBO.departments))
        result = await self.session.execute(stmt)
        dbos = result.scalars().all()

        return [await self.mapper.dbo_to_entity(dbo) for dbo in dbos]

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        stmt = (
            select(UserDBO)
            .options(selectinload(UserDBO.departments))
            .where(UserDBO.id == user_id)
        )
        result = await self.session.execute(stmt)
        dbo = result.scalar_one_or_none()

        if dbo is None:
            return None

        return await self.mapper.dbo_to_entity(dbo)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        stmt = (
            select(UserDBO)
            .options(selectinload(UserDBO.departments))
            .where(UserDBO.email == email)
        )
        result = await self.session.execute(stmt)
        dbo = result.scalar_one_or_none()

        if dbo is None:
            return None

        return await self.mapper.dbo_to_entity(dbo)

    async def update(self, user: User) -> User:
        """Update an existing user."""
        stmt = (
            select(UserDBO)
            .options(selectinload(UserDBO.departments))
            .where(UserDBO.id == user.id)
        )
        result = await self.session.execute(stmt)
        dbo = result.scalar_one_or_none()

        if dbo is None:
            raise ValueError(f"User with id {user.id} not found")

        # Update fields
        dbo.first_name = user.first_name
        dbo.last_name = user.last_name
        dbo.email = user.email
        dbo.is_active = user.is_active

        # Update departments
        if user.departments is not None:
            department_names = [dept.name for dept in user.departments]
            departments = []

            for dept_name in department_names:
                stmt_dept = select(DepartmentDBO).where(DepartmentDBO.name == dept_name)
                result_dept = await self.session.execute(stmt_dept)
                dept = result_dept.scalar_one_or_none()

                if not dept:
                    dept = DepartmentDBO(name=dept_name)
                    self.session.add(dept)
                    await self.session.flush()

                departments.append(dept)

            dbo.departments = departments

        await self.session.flush()
        await self.session.refresh(dbo, ["departments"])

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
