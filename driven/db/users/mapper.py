"""Mapper between User entities and database objects."""

from typing import Optional
from domain.entities.users import User, Department
from driven.db.users.models import UserDBO, DepartmentDBO


class UserDBOMapper:
    """Maps between User domain entities and UserDBO database objects."""

    async def entity_to_dbo(self, entity: User) -> UserDBO:
        """Convert User entity to UserDBO."""
        dbo = UserDBO(
            first_name=entity.first_name or "",
            last_name=entity.last_name or "",
            email=entity.email,
            is_active=entity.is_active if hasattr(entity, 'is_active') else True,
        )

        # Set ID if entity has one (for updates)
        if hasattr(entity, 'id') and entity.id is not None:
            dbo.id = entity.id

        return dbo

    async def dbo_to_entity(self, dbo: UserDBO) -> User:
        """Convert UserDBO to User entity."""
        # Map departments
        departments = []
        if dbo.departments:
            for dept in dbo.departments:
                departments.append(Department(id=dept.id, name=dept.name))

        return User(
            id=dbo.id,
            first_name=dbo.first_name,
            last_name=dbo.last_name,
            email=dbo.email,
            is_active=dbo.is_active,
            departments=departments,
        )


class DepartmentDBOMapper:
    """Maps between Department entities and DepartmentDBO database objects."""

    async def entity_to_dbo(self, entity: Department) -> DepartmentDBO:
        """Convert Department entity to DepartmentDBO."""
        dbo = DepartmentDBO(name=entity.name)

        if hasattr(entity, 'id') and entity.id is not None:
            dbo.id = entity.id

        return dbo

    async def dbo_to_entity(self, dbo: DepartmentDBO) -> Department:
        """Convert DepartmentDBO to Department entity."""
        return Department(
            id=dbo.id,
            name=dbo.name,
        )
