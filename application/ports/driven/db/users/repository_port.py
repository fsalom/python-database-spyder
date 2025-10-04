"""User repository port interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.user import User


class UsersRepositoryPort(ABC):
    """Port interface for User repository operations."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> List[User]:
        """Get all users."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Delete a user."""
        raise NotImplementedError
