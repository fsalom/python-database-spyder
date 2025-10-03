"""Users service implementation."""

import logging
from typing import List, Optional

from application.ports.driven.db.users.repository_port import UsersRepositoryPort
from application.ports.driving.users.service_port import UsersServicePort
from domain.entities.users import User


class UsersService(UsersServicePort):
    """Application service for User business logic."""

    def __init__(
        self,
        users_repository: UsersRepositoryPort,
    ):
        self.users_repository = users_repository

    async def get_all_users(self) -> List[User]:
        """Get all users."""
        return await self.users_repository.get_all()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return await self.users_repository.get_by_id(user_id)

    async def get_or_create_user(self, email: str) -> User:
        """
        Get or create a user by email.

        Args:
            email: User email address

        Returns:
            User entity
        """
        # Check if user with email already exists
        existing_user = await self.users_repository.get_by_email(email)
        if existing_user:
            logging.info(f"User {email} already exists")
            return existing_user

        # Create new user
        new_user = User(email=email)
        created_user = await self.users_repository.create(new_user)
        logging.info(f"Created new user {email}")
        return created_user

    async def create_user(self, user: User) -> User:
        """Create a new user."""
        return await self.users_repository.create(user)

    async def update_user(self, user: User) -> User:
        """Update an existing user."""
        return await self.users_repository.update(user)

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        return await self.users_repository.delete(user_id)
