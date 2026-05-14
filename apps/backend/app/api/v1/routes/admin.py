from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_admin
from app.db_models.user import User
from app.db_models.stream_session import StreamSession
from app.db_models.anomaly_event import AnomalyEvent
from app.db_models.alert_notification import AlertNotification
from app.schemas.admin import AdminOverview, AdminUserRead, AdminUserUpdate
from app.services.inference.registry import detector_registry

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=list[AdminUserRead])
def list_users(db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()

@router.patch("/users/{user_id}", response_model=AdminUserRead)
def update_user(user_id: int, payload: AdminUserUpdate, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy user.")
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.is_superuser is not None:
        user.is_superuser = payload.is_superuser
    db.commit()
    db.refresh(user)
    return user

@router.get('/overview', response_model=AdminOverview)
def overview(db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    return AdminOverview(
        total_users=db.query(func.count(User.id)).scalar() or 0,
        active_users=db.query(func.count(User.id)).filter(User.is_active.is_(True)).scalar() or 0,
        total_sessions=db.query(func.count(StreamSession.id)).scalar() or 0,
        running_sessions=db.query(func.count(StreamSession.id)).filter(StreamSession.status == 'running').scalar() or 0,
        total_events=db.query(func.count(AnomalyEvent.id)).scalar() or 0,
        total_notifications=db.query(func.count(AlertNotification.id)).scalar() or 0,
        loaded_models=detector_registry.list_keys(),
    )
