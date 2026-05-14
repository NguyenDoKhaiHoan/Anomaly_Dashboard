from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class AlertRuleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    stream_type: str | None = None
    asset_symbol: str | None = None
    score_threshold: float = 0.5
    consecutive_count: int = Field(default=1, ge=1, le=20)
    channel: str = "in_app"
    phone_number: str | None = None
    fcm_token: str | None = None

class AlertRuleRead(BaseModel):
    id: int
    user_id: int
    name: str
    stream_type: str | None
    asset_symbol: str | None
    score_threshold: float
    consecutive_count: int
    channel: str
    phone_number: str | None
    fcm_token: str | None
    is_enabled: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AlertNotificationRead(BaseModel):
    id: int
    user_id: int
    rule_id: int | None
    anomaly_event_id: int | None
    level: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
