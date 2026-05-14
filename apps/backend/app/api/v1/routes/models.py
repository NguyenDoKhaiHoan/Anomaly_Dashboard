from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.db_models.model_registry import ModelRegistry
from app.services.inference.registry import detector_registry

router = APIRouter(prefix="/models", tags=["models"])

@router.get("")
def list_models(db: Session = Depends(get_db)):
    rows = db.query(ModelRegistry).order_by(ModelRegistry.stream_type, ModelRegistry.name).all()
    result = []
    for row in rows:
        model_info = {
            "key": row.key, 
            "name": row.name, 
            "stream_type": row.stream_type, 
            "model_type": row.model_type,
            "artifact_path": row.artifact_path, 
            "metadata": row.metadata_json, 
            "is_enabled": row.is_enabled
        }
        
        # Add runtime config from loaded detector
        if row.key in detector_registry.list_keys():
            detector = detector_registry.get(row.key)
            runtime_config = {}
            if hasattr(detector, 'default_threshold'):
                runtime_config = {
                    "threshold": detector.default_threshold,
                    "rolling_window": getattr(detector, 'rolling_window', 50),
                    "ema_span": getattr(detector, 'ema_span', 20),
                    "zscore_features": getattr(detector, 'zscore_features', []),
                    "extra_features": getattr(detector, 'extra_features', []),
                }
                # Flatten threshold for backward compatibility
                model_info["threshold"] = detector.default_threshold
                if hasattr(detector, 'best_f1'):
                    runtime_config["best_f1"] = detector.best_f1
                if hasattr(detector, 'zscore_weight'):
                    runtime_config["weights"] = {
                        "zscore": detector.zscore_weight,
                        "city": detector.city_weight,
                        "ema_diff": detector.ema_diff_weight,
                        "ema_gap_mult": detector.ema_gap_mult
                    }
            model_info["runtime_config"] = runtime_config
        
        result.append(model_info)
    return result
