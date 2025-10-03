"""User API request models."""

from typing import List, Optional
from pydantic import BaseModel, EmailStr


class CreateUserRequest(BaseModel):
    """Request model for creating a user."""

    email: EmailStr
    first_name: str = ""
    last_name: str = ""
    is_active: bool = True
    department_names: List[str] = []


class UpdateUserRequest(BaseModel):
    """Request model for updating a user."""

    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    department_names: Optional[List[str]] = None
