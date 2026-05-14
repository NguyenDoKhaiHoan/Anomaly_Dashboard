from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class StreamSessionCreate(BaseModel):
    stream_type: str = Field(pattern="^(credit_card|iot_sensor)$")
    model_key: str
    dataset_key: str | None = None
    asset_symbol: str | None = None
    stream_interval: float = Field(default=1.0, ge=0.2, le=10.0)
    threshold_override: float | None = None

class StreamSessionRead(BaseModel):
    id: str
    user_id: int
    stream_type: str
    model_key: str
    dataset_key: str | None
    asset_symbol: str | None
    status: str
    stream_interval: float
    threshold_override: float | None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class StreamControlResponse(BaseModel):
    session_id: str
    status: str
    active_sessions: int
    queue_size: int

class StreamEvent(BaseModel):
    session_id: str
    stream_type: str
    model_key: str
    timestamp: datetime
    raw_event: dict[str, Any]
    features: dict[str, Any]
    anomaly_score: float
    is_anomaly: bool
    reasons: list[str]
    detector_latency_ms: float
    summary: dict[str, Any]

class SessionSummary(BaseModel):
    total_events: int
    total_anomalies: int
    running: bool
    latest_score: float | None = None
