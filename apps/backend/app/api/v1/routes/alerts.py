from __future__ import annotations
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.db_models.alert_notification import AlertNotification
from app.db_models.alert_rule import AlertRule
from app.schemas.alert import AlertNotificationRead, AlertRuleCreate, AlertRuleRead

router = APIRouter(prefix="/alerts", tags=["alerts"])

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

@router.get("/rules", response_model=list[AlertRuleRead])
def list_rules(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(AlertRule).filter(AlertRule.user_id == current_user.id).order_by(AlertRule.created_at.desc()).all()

@router.post("/rules", response_model=AlertRuleRead)
def create_rule(payload: AlertRuleCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    rule = AlertRule(user_id=current_user.id, **payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.get("/notifications", response_model=list[AlertNotificationRead])
def list_notifications(
    period: str = Query("all", description="Filter: all, today, week, month, year"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(AlertNotification).filter(AlertNotification.user_id == current_user.id)
    period_start = _get_period_start(period)
    if period_start:
        query = query.filter(AlertNotification.created_at >= period_start)
    return query.order_by(AlertNotification.created_at.desc()).limit(100).all()

@router.delete("/rules/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    row = db.query(AlertRule).filter(
        AlertRule.id == rule_id,
        AlertRule.user_id == current_user.id
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy rule.")
    db.delete(row)
    db.commit()
    return {"message": "Đã xóa rule."}

@router.delete("/notifications/{notification_id}")
def delete_notification(notification_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    row = db.query(AlertNotification).filter(
        AlertNotification.id == notification_id,
        AlertNotification.user_id == current_user.id
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy notification.")
    db.delete(row)
    db.commit()
    return {"message": "Đã xóa notification."}

@router.post("/notifications/{notification_id}/read", response_model=AlertNotificationRead)
def mark_read(notification_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    row = db.query(AlertNotification).filter(AlertNotification.id == notification_id, AlertNotification.user_id == current_user.id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy notification.")
    row.is_read = True
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
