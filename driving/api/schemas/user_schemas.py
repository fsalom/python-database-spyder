"""Pydantic schemas for User API."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreateRequest(BaseModel):
    """Schema for creating a user via API."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: Optional[str] = None
    is_superuser: bool = False


class UserUpdateRequest(BaseModel):
    """Schema for updating a user via API."""

    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UsersListResponse(BaseModel):
    """Schema for users list response."""

    users: list[UserResponse]
    total: int
