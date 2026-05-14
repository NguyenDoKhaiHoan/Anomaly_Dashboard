from __future__ import annotations
from pydantic import BaseModel


class DatasetRead(BaseModel):
    key: str
    name: str
    stream_type: str
    source_type: str
    path: str | None = None
    description: str | None = None
    is_enabled: bool
    recommended_threshold: float | None = None


class AssetRead(BaseModel):
    symbol: str
    name: str
    asset_type: str
    is_enabled: bool