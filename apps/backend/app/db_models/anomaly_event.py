from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("stream_sessions.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    stream_type: Mapped[str] = mapped_column(String(50), index=True)
    asset_symbol: Mapped[str | None] = mapped_column(String(32), nullable=True)
    model_key: Mapped[str] = mapped_column(String(100), index=True)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    raw_payload: Mapped[dict] = mapped_column(JSON)
    feature_payload: Mapped[dict] = mapped_column(JSON)
    anomaly_score: Mapped[float] = mapped_column(Float, default=0.0)
    is_anomaly: Mapped[bool] = mapped_column(Boolean, default=False)
    reasons: Mapped[list] = mapped_column(JSON, default=list)
    detector_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)

    session = relationship("StreamSession", back_populates="anomaly_events")
    user = relationship("User", back_populates="anomaly_events")
