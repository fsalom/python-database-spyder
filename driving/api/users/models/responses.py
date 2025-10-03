"""User API response models."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class DepartmentResponse(BaseModel):
    """Department response model."""

    id: int
    name: str

    class Config:
        from_attributes = True


class BaseUserResponse(BaseModel):
    """Base user response model."""

    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool

    class Config:
        from_attributes = True


class UserResponse(BaseUserResponse):
    """Full user response model."""

    id: int
    departments: List[DepartmentResponse] = []

    class Config:
        from_attributes = True
