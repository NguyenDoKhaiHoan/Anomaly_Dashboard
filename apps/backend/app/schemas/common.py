from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict

class APIMessage(BaseModel):
    message: str

class HealthResponse(BaseModel):
    status: str
    app_name: str
    loaded_models: list[str]
    model_configs: dict[str, Any] = {}
    active_sessions: int
    server_time: datetime

class PaginationMeta(BaseModel):
    total: int
    limit: int
    offset: int

class PaginatedItems(BaseModel):
    items: list[Any]
    meta: PaginationMeta
    model_config = ConfigDict(arbitrary_types_allowed=True)
