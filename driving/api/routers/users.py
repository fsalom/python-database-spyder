"""FastAPI router for users management."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from driven.db.users.adapter import UsersDBRepositoryAdapter
from application.services.users_service import UsersService
from domain.entities.user import UserCreate, UserUpdate
from driving.api.schemas.user_schemas import (
    UserResponse,
    UserCreateRequest,
    UserUpdateRequest,
    UsersListResponse,
)
from driving.api.routers.auth import get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])


def get_users_service(db: AsyncSession = Depends(get_db)) -> UsersService:
    """Dependency to get users service."""
    users_repo = UsersDBRepositoryAdapter(db)
    return UsersService(users_repo)


async def get_current_superuser(
    current_user = Depends(get_current_active_user),
):
    """Dependency to ensure current user is a superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


@router.get("", response_model=UsersListResponse)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_superuser),
    service: UsersService = Depends(get_users_service),
):
    """Get all users (superuser only)."""
    users = await service.get_all_users(skip=skip, limit=limit)
    total = len(users)  # In production, you'd want a proper count
    
    return UsersListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    current_user = Depends(get_current_superuser),
    service: UsersService = Depends(get_users_service),
):
    """Create a new user (superuser only)."""
    try:
        user_create = UserCreate(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            is_superuser=user_data.is_superuser,
        )
        
        user = await service.create_user(user_create)
        return UserResponse.model_validate(user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user = Depends(get_current_active_user),
    service: UsersService = Depends(get_users_service),
):
    """Get a specific user."""
    # Users can only view themselves unless they're superuser
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    current_user = Depends(get_current_active_user),
    service: UsersService = Depends(get_users_service),
):
    """Update a user."""
    # Users can only update themselves unless they're superuser
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Only superusers can change is_superuser status
    if user_data.is_superuser is not None and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can modify superuser status"
        )
    
    try:
        user_update = UserUpdate(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            is_active=user_data.is_active,
            is_superuser=user_data.is_superuser,
        )
        
        user = await service.update_user(user_id, user_update)
        return UserResponse.model_validate(user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user = Depends(get_current_superuser),
    service: UsersService = Depends(get_users_service),
):
    """Delete a user (superuser only)."""
    # Prevent superuser from deleting themselves
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    success = await service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
