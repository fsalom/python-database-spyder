"""Pydantic schemas for Authentication API."""

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema."""

    email: str | None = None


class LoginRequest(BaseModel):
    """Login request schema."""

    username: EmailStr  # Using email as username
    password: str


class RegisterRequest(BaseModel):
    """Registration request schema."""

    email: EmailStr
    password: str
    full_name: str | None = None
