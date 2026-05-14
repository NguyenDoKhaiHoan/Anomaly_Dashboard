from __future__ import annotations
from fastapi import APIRouter
from app.core.config import settings
from app.schemas.common import HealthResponse
from app.services.inference.registry import detector_registry
from app.services.stream.session_manager import session_manager
from app.utils.time import utc_now

router = APIRouter(prefix="/health", tags=["health"])

def _detector_config(detector) -> dict:
    config = {
        "threshold": getattr(detector, 'default_threshold', None),
        "rolling_window": getattr(detector, 'rolling_window', None),
        "ema_span": getattr(detector, 'ema_span', None),
        "zscore_features": getattr(detector, 'zscore_features', None),
        "extra_features": getattr(detector, 'extra_features', None),
    }
    if hasattr(detector, 'best_f1'):
        config["best_f1"] = detector.best_f1
    if hasattr(detector, 'zscore_weight'):
        config["weights"] = {
            "zscore": detector.zscore_weight,
            "city": detector.city_weight,
            "ema_diff": detector.ema_diff_weight,
            "ema_gap_mult": detector.ema_gap_mult
        }
    return config

@router.get("", response_model=HealthResponse)
def health():
    model_configs = {}
    for key in detector_registry.list_keys():
        model_configs[key] = _detector_config(detector_registry.get(key))
    
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        loaded_models=detector_registry.list_keys(),
        model_configs=model_configs,
        active_sessions=session_manager.active_count(),
        server_time=utc_now(),
    )
