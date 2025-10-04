"""Users management service."""

from typing import List, Optional

from config.security import get_password_hash
from domain.entities.user import User, UserCreate, UserUpdate
from application.ports.driven.db.users.repository_port import UsersRepositoryPort


class UsersService:
    """Service for managing users."""

    def __init__(self, users_repo: UsersRepositoryPort):
        self.users_repo = users_repo

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = await self.users_repo.get_by_email(user_data.email)
        if existing_user:
            raise ValueError(f"User with email {user_data.email} already exists")

        # Create user with hashed password
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_superuser=user_data.is_superuser,
            is_active=True,
        )

        return await self.users_repo.create(user)

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users."""
        users = await self.users_repo.get_all()
        return users[skip : skip + limit]

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return await self.users_repo.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return await self.users_repo.get_by_email(email)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update an existing user."""
        user = await self.users_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        # Update fields if provided
        if user_data.email is not None:
            # Check if new email is already taken
            if user_data.email != user.email:
                existing = await self.users_repo.get_by_email(user_data.email)
                if existing:
                    raise ValueError(f"Email {user_data.email} already in use")
            user.email = user_data.email

        if user_data.full_name is not None:
            user.full_name = user_data.full_name

        if user_data.password is not None:
            user.hashed_password = get_password_hash(user_data.password)

        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        if user_data.is_superuser is not None:
            user.is_superuser = user_data.is_superuser

        return await self.users_repo.update(user)

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        return await self.users_repo.delete(user_id)

    async def create_superuser_if_not_exists(
        self, email: str, password: str, full_name: str = "Admin"
    ) -> Optional[User]:
        """Create initial superuser if it doesn't exist."""
        existing = await self.users_repo.get_by_email(email)
        if existing:
            return None

        user_data = UserCreate(
            email=email,
            password=password,
            full_name=full_name,
            is_superuser=True,
        )

        return await self.create_user(user_data)
