from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class StreamSession(Base):
    __tablename__ = "stream_sessions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    stream_type: Mapped[str] = mapped_column(String(50), index=True)
    model_key: Mapped[str] = mapped_column(String(100), index=True)
    dataset_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    asset_symbol: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="created")
    stream_interval: Mapped[float] = mapped_column(Float, default=1.0)
    threshold_override: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="sessions")
    anomaly_events = relationship("AnomalyEvent", back_populates="session")
