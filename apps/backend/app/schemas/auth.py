from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: str | None = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: str
    full_name: str | None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v):
        """Ensure id is always an integer"""
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                raise ValueError("ID phải là số nguyên")
        return int(v)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
