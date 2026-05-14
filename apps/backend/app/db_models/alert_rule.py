from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class AlertRule(Base):
    __tablename__ = "alert_rules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    stream_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    asset_symbol: Mapped[str | None] = mapped_column(String(32), nullable=True)
    score_threshold: Mapped[float] = mapped_column(Float, default=0.5)
    consecutive_count: Mapped[int] = mapped_column(Integer, default=1)
    channel: Mapped[str] = mapped_column(String(50), default="in_app")
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fcm_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="alert_rules")
    notifications = relationship("AlertNotification", back_populates="rule")
