"""Authentication service."""

from datetime import timedelta
from typing import Optional

from config.security import create_access_token, verify_password, get_password_hash
from config.settings import settings
from domain.entities.user import User, UserCreate
from application.ports.driven.db.users.repository_port import UsersRepositoryPort


class AuthService:
    """Service for authentication operations."""

    def __init__(self, users_repo: UsersRepositoryPort):
        self.users_repo = users_repo

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = await self.users_repo.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def create_access_token_for_user(self, user: User) -> str:
        """Create access token for a user."""
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        return create_access_token(
            subject=user.email, expires_delta=access_token_expires
        )

    async def register_user(self, user_data: UserCreate) -> User:
        """Register a new user."""
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

    async def get_current_user_from_token(self, token: str) -> Optional[User]:
        """Get current user from JWT token."""
        from jose import jwt, JWTError
        
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            email: str = payload.get("sub")
            if email is None:
                return None
        except JWTError:
            return None

        user = await self.users_repo.get_by_email(email)
        return user
