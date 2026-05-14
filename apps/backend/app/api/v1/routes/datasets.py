from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json
import os

from app.core.database import get_db
from app.db_models.asset import Asset
from app.db_models.dataset_registry import DatasetRegistry
from app.schemas.dataset import DatasetRead, AssetRead

router = APIRouter(prefix="/datasets", tags=["datasets"])

# Threshold mapping by stream_type from model metadata files
THRESHOLD_BY_TYPE = None

# Map stream_type (DB) -> folder name (models)
STREAM_TYPE_TO_FOLDER = {
    "credit_card": "fraud",
    "iot_sensor": "iot",
}

def _load_thresholds():
    global THRESHOLD_BY_TYPE
    if THRESHOLD_BY_TYPE is not None:
        return THRESHOLD_BY_TYPE
    THRESHOLD_BY_TYPE = {}
    # Path: apps/backend/app/api/v1/routes/ -> 6 levels up = Project2/, then models/
    base = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "..", "models")
    for folder, meta_file in [("fraud", "metadata.json"), ("iot", "metadata.json")]:
        path = os.path.join(base, folder, meta_file)
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
                THRESHOLD_BY_TYPE[folder] = data.get("threshold")
    return THRESHOLD_BY_TYPE


@router.get("", response_model=list[DatasetRead])
def list_datasets(db: Session = Depends(get_db)):
    _load_thresholds()
    rows = db.query(DatasetRegistry).order_by(
        DatasetRegistry.stream_type,
        DatasetRegistry.name
    ).all()

    return [
        DatasetRead(
            key=row.key,
            name=row.name,
            stream_type=row.stream_type,
            source_type=row.source_type,
            path=row.path,
            description=row.description,
            is_enabled=row.is_enabled,
            recommended_threshold=THRESHOLD_BY_TYPE.get(STREAM_TYPE_TO_FOLDER.get(row.stream_type, row.stream_type)),
        )
        for row in rows
    ]


@router.get("/assets", response_model=list[AssetRead])
def list_assets(db: Session = Depends(get_db)):
    rows = db.query(Asset).order_by(Asset.symbol).all()

    return [
        AssetRead(
            symbol=row.symbol,
            name=row.name,
            asset_type=row.asset_type,
            is_enabled=row.is_enabled,
        )
        for row in rows
    ]