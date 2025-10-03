"""User domain entities."""

from typing import List, Optional
from pydantic import BaseModel, EmailStr


class Department(BaseModel):
    """Department domain entity."""

    id: Optional[int] = None
    name: str

    class Config:
        from_attributes = True


class BaseUser(BaseModel):
    """Base user entity with common fields."""

    first_name: str = ""
    last_name: str = ""
    email: EmailStr
    is_active: bool = True

    class Config:
        from_attributes = True


class User(BaseUser):
    """Full user entity with all fields."""

    id: Optional[int] = None
    departments: List[Department] = []

    class Config:
        from_attributes = True
