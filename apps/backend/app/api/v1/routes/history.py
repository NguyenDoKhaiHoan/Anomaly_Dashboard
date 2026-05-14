from __future__ import annotations
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.common import PaginationMeta
from app.services.history.query_service import list_anomaly_events, export_anomaly_events_to_csv

router = APIRouter(prefix="/history", tags=["history"])

def serialize_datetime(dt):
    """Convert datetime to ISO string with timezone for consistent frontend parsing."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

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

@router.get("/events")
def history_events(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    stream_type: str | None = None,
    session_id: str | None = None,
    period: str = Query(default="all", description="Filter: all, today, week, month, year"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    items, total = list_anomaly_events(
        db=db, user_id=current_user.id, limit=limit, offset=offset,
        stream_type=stream_type, session_id=session_id, period=period
    )
    return {
        "items": [{
            "id": item.id, "session_id": item.session_id, "stream_type": item.stream_type, "model_key": item.model_key,
            "event_timestamp": serialize_datetime(item.event_timestamp), "anomaly_score": item.anomaly_score, "is_anomaly": item.is_anomaly,
            "reasons": item.reasons, "raw_payload": item.raw_payload, "feature_payload": item.feature_payload,
            "detector_latency_ms": item.detector_latency_ms,
        } for item in items],
        "meta": PaginationMeta(total=total, limit=limit, offset=offset).model_dump(),
    }

@router.get("/events/export")
def export_events_csv(
    stream_type: str | None = None,
    session_id: str | None = None,
    period: str = Query(default="all", description="Filter: all, today, week, month, year"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    csv_buffer = export_anomaly_events_to_csv(
        db=db, user_id=current_user.id, stream_type=stream_type,
        session_id=session_id, period=period
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"anomaly_events_{timestamp}.csv"
    return StreamingResponse(
        iter([csv_buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
