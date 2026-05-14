from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import admin, alerts, auth, datasets, health, history, models, streams
from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.core.logging import logger
from app.db_models.user import User
from app.core.security import hash_password
from app.services.inference.registry import detector_registry

def seed_initial_data() -> None:
    db = SessionLocal()
    try:
        detector_registry.sync_registry_to_database(db)
        demo_user = db.query(User).filter(User.username == "demo").first()
        if demo_user is None:
            db.add(User(username="demo", email="demo@example.com", full_name="Demo User", hashed_password=hash_password("demo123"), is_superuser=True))
        db.commit()
    finally:
        db.close()

def _init_fcm():
    try:
        from pathlib import Path
        cred_path = Path(__file__).parent.parent.parent.parent / "scripts" / "fcm-firebase-8c77f-firebase-adminsdk-fbsvc-3cf455fbcd.json"
        if cred_path.exists():
            from app.services.notification.fcm_service import FCMService
            FCMService.get_instance(str(cred_path))
            logger.info("FCM service initialized")
        else:
            logger.warning(f"FCM credentials not found at {cred_path}")
    except Exception as e:
        logger.warning(f"FCM initialization skipped: {e}")


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
    app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
    app.include_router(streams.router, prefix=settings.API_V1_PREFIX)
    app.include_router(models.router, prefix=settings.API_V1_PREFIX)
    app.include_router(alerts.router, prefix=settings.API_V1_PREFIX)
    app.include_router(history.router, prefix=settings.API_V1_PREFIX)
    app.include_router(datasets.router, prefix=settings.API_V1_PREFIX)
    app.include_router(health.router, prefix=settings.API_V1_PREFIX)

    @app.on_event("startup")
    async def startup_event() -> None:
        logger.info("Initializing database...")
        init_db()
        logger.info("Loading detectors...")
        detector_registry.load_builtin_detectors()
        _init_fcm()
        seed_initial_data()

    @app.get("/")
    def root():
        return {"app": settings.APP_NAME, "docs": "/docs", "api_prefix": settings.API_V1_PREFIX, "loaded_models": detector_registry.list_keys()}

    return app


app = create_app()
