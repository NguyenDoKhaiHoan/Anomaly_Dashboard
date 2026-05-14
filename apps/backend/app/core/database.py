from __future__ import annotations

from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

class Base(DeclarativeBase):
    pass

engine = create_engine(settings.sqlalchemy_database_uri, echo=False, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    from app.db_models import alert_notification, alert_rule, anomaly_event, asset, dataset_registry, model_registry, stream_session, user  # noqa: F401
    Base.metadata.create_all(bind=engine)
