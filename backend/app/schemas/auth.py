"""Pydantic schemas for authentication."""
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Registration request."""
    email: str = Field(..., min_length=5, max_length=255)
    full_name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    """Login request."""
    email: str
    password: str


class UserResponse(BaseModel):
    """User profile response."""
    id: str
    email: str
    full_name: str
    is_active: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
