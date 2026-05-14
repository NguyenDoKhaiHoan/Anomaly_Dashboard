from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class ModelRegistry(Base):
    __tablename__ = "model_registry"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    stream_type: Mapped[str] = mapped_column(String(50), index=True)
    model_type: Mapped[str] = mapped_column(String(50), index=True)
    artifact_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
