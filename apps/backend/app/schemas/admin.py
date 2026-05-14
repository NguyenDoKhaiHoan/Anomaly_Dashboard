from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, EmailStr

class AdminUserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str | None = None
    is_active: bool
    is_superuser: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class AdminUserUpdate(BaseModel):
    is_active: bool | None = None
    is_superuser: bool | None = None

class AdminOverview(BaseModel):
    total_users: int
    active_users: int
    total_sessions: int
    running_sessions: int
    total_events: int
    total_notifications: int
    loaded_models: list[str]
