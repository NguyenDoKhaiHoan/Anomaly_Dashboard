from __future__ import annotations
import csv
import io
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db_models.anomaly_event import AnomalyEvent

def _get_period_start(period: str):
    now = datetime.now(timezone.utc)
    if period == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        return now - timedelta(days=now.weekday())
    elif period == "month":
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "year":
        return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return None

def list_anomaly_events(db: Session, user_id: int, limit: int = 100, offset: int = 0, stream_type: str | None = None, session_id: str | None = None, period: str = "all"):
    query = db.query(AnomalyEvent).filter(AnomalyEvent.user_id == user_id)
    period_start = _get_period_start(period)
    if period_start:
        query = query.filter(AnomalyEvent.event_timestamp >= period_start)
    if stream_type:
        query = query.filter(AnomalyEvent.stream_type == stream_type)
    if session_id:
        query = query.filter(AnomalyEvent.session_id == session_id)
    total = query.count()
    items = query.order_by(AnomalyEvent.event_timestamp.desc()).offset(offset).limit(limit).all()
    return items, total

def export_anomaly_events_to_csv(db: Session, user_id: int, stream_type: str | None = None, session_id: str | None = None, period: str = "all") -> io.StringIO:
    query = db.query(AnomalyEvent).filter(AnomalyEvent.user_id == user_id)
    period_start = _get_period_start(period)
    if period_start:
        query = query.filter(AnomalyEvent.event_timestamp >= period_start)
    if stream_type:
        query = query.filter(AnomalyEvent.stream_type == stream_type)
    if session_id:
        query = query.filter(AnomalyEvent.session_id == session_id)
    
    items = query.order_by(AnomalyEvent.event_timestamp.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "ID", "Session ID", "Stream Type", "Model Key", "Timestamp",
        "Anomaly Score", "Is Anomaly", "Reasons", "Latency (ms)"
    ])
    
    for item in items:
        timestamp = item.event_timestamp.strftime("%Y-%m-%d %H:%M:%S") if item.event_timestamp else ""
        reasons = "; ".join(item.reasons) if item.reasons else ""
        writer.writerow([
            item.id,
            item.session_id,
            item.stream_type,
            item.model_key,
            timestamp,
            f"{item.anomaly_score:.4f}" if item.anomaly_score else "",
            "Yes" if item.is_anomaly else "No",
            reasons,
            f"{item.detector_latency_ms:.2f}" if item.detector_latency_ms else "",
        ])
    
    output.seek(0)
    return output
