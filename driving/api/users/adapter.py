"""FastAPI adapter for Users operations."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from application.di.dependencies import get_users_service
from application.ports.driving.users.api_port import UsersAPIPort
from application.services.users_service import UsersService
from domain.entities.users import User
from driving.api.users.mapper import UsersAPIMapper
from driving.api.users.models.responses import UserResponse
from driving.api.users.models.requests import CreateUserRequest, UpdateUserRequest


class UsersAPIAdapter(UsersAPIPort):
    """FastAPI adapter for Users operations with dependency injection."""

    def __init__(self):
        self.router = APIRouter()
        self.mapper = UsersAPIMapper()
        self._register_routes()

    def _register_routes(self):
        """Register all routes."""

        @self.router.get("/", response_model=List[UserResponse])
        async def get_all_users(
            users_service: UsersService = Depends(get_users_service),
        ) -> List[UserResponse]:
            """Get all users."""
            users = await users_service.get_all_users()
            return [self.mapper.entity_to_response(user) for user in users]

        @self.router.get("/{user_id}", response_model=UserResponse)
        async def get_user_by_id(
            user_id: int,
            users_service: UsersService = Depends(get_users_service),
        ) -> UserResponse:
            """Get user by ID."""
            user = await users_service.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {user_id} not found",
                )
            return self.mapper.entity_to_response(user)

        @self.router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
        async def create_user(
            request_data: CreateUserRequest,
            users_service: UsersService = Depends(get_users_service),
        ) -> UserResponse:
            """Create a new user."""
            user = self.mapper.request_to_entity(request_data)
            created_user = await users_service.create_user(user)
            return self.mapper.entity_to_response(created_user)

        @self.router.put("/{user_id}", response_model=UserResponse)
        async def update_user(
            user_id: int,
            request_data: UpdateUserRequest,
            users_service: UsersService = Depends(get_users_service),
        ) -> UserResponse:
            """Update an existing user."""
            # Check if user exists
            existing_user = await users_service.get_user_by_id(user_id)
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {user_id} not found",
                )

            # Update fields
            update_data = request_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(existing_user, field, value)

            updated_user = await users_service.update_user(existing_user)
            return self.mapper.entity_to_response(updated_user)

        @self.router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_user(
            user_id: int,
            users_service: UsersService = Depends(get_users_service),
        ):
            """Delete a user."""
            success = await users_service.delete_user(user_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {user_id} not found",
                )
            return None
