"""Mapper between User entities and database objects."""

from domain.entities.user import User
from driven.db.users.models import UserDBO


class UserDBOMapper:
    """Maps between User domain entities and UserDBO database objects."""

    async def entity_to_dbo(self, entity: User) -> UserDBO:
        """Convert User entity to UserDBO."""
        dbo = UserDBO(
            email=entity.email,
            full_name=entity.full_name,
            hashed_password=entity.hashed_password,
            is_active=entity.is_active,
            is_superuser=entity.is_superuser,
        )

        if hasattr(entity, 'id') and entity.id is not None:
            dbo.id = entity.id

        return dbo

    async def dbo_to_entity(self, dbo: UserDBO) -> User:
        """Convert UserDBO to User entity."""
        return User(
            id=dbo.id,
            email=dbo.email,
            full_name=dbo.full_name,
            hashed_password=dbo.hashed_password,
            is_active=dbo.is_active,
            is_superuser=dbo.is_superuser,
            created_at=dbo.created_at,
            updated_at=dbo.updated_at,
        )
