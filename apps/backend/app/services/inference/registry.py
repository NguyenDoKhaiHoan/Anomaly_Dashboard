from __future__ import annotations
import json
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.db_models.dataset_registry import DatasetRegistry
from app.db_models.model_registry import ModelRegistry
from app.services.inference.fraud_statistical import FraudStatisticalDetector
from app.services.inference.iot_lstm import IoTLSTMDetector

BUILTIN_MODELS = [
    {
        "key": "fraud_statistical",
        "name": "Fraud Statistical Detector",
        "stream_type": "credit_card",
        "model_type": "statistical",
        "artifact_path": "models/fraud/statistical_fraud_model.pkl",
        "metadata_json": {"source": "uploaded_bundle", "notes": "Threshold/EMA/Z-score based detector."},
    },
    {
        "key": "iot_lstm",
        "name": "IoT LSTM Sequence Classifier",
        "stream_type": "iot_sensor",
        "model_type": "lstm_sequence",
        "artifact_path": "models/iot/iot_lstm_full_bundle.pt",
        "metadata_json": {"source": "uploaded_bundle", "notes": "Sequence model using sliding window inference."},
    },
]

BUILTIN_DATASETS = [
    {
        "key": "credit_card_sample",
        "name": "Credit Card Sample Stream",
        "stream_type": "credit_card",
        "source_type": "csv",
        "path": "data/samples/credit_card_sample.csv",
        "description": "Sample credit-card transaction stream.",
    },
    {
        "key": "iot_raw",
        "name": "IoT Raw Data",
        "stream_type": "iot_sensor",
        "source_type": "csv",
        "path": "data/raw/iot/iot.csv",
        "description": "Raw IoT data stream from data/raw/iot/iot.csv.",
    },
]

class DetectorRegistry:
    def __init__(self):
        self._detectors = {}

    def load_builtin_detectors(self):
        # Load fraud detector - use metadata.json (statistical_fraud_model.pkl may not exist)
        fraud_bundle_path = settings.MODELS_DIR / "fraud" / "metadata.json"
        if not fraud_bundle_path.exists():
            fraud_bundle_path = settings.MODELS_DIR / "fraud" / "statistical_fraud_model.pkl"
        self._detectors["fraud_statistical"] = FraudStatisticalDetector(fraud_bundle_path)
        
        # Load LSTM detector
        lstm_detector = IoTLSTMDetector(settings.MODELS_DIR / "iot" / "iot_lstm_full_bundle.pt")
        if lstm_detector.loaded:
            self._detectors["iot_lstm"] = lstm_detector
            logger.info("IoT LSTM detector loaded successfully")
        else:
            logger.warning("IoT LSTM model not found at models/iot/iot_lstm_full_bundle.pt - using statistical fallback")
        
        logger.info("Loaded detectors: %s", list(self._detectors.keys()))

    def get(self, key: str):
        if key not in self._detectors:
            raise KeyError(f"Không tìm thấy detector: {key}")
        return self._detectors[key]

    def list_keys(self):
        return list(self._detectors.keys())

    def sync_registry_to_database(self, db: Session):
        for item in BUILTIN_MODELS:
            exists = db.query(ModelRegistry).filter(ModelRegistry.key == item["key"]).first()
            if exists is None:
                db.add(ModelRegistry(**item))
        for item in BUILTIN_DATASETS:
            exists = db.query(DatasetRegistry).filter(DatasetRegistry.key == item["key"]).first()
            if exists is None:
                db.add(DatasetRegistry(**item))
        db.commit()
        registry_payload = {"models": BUILTIN_MODELS, "datasets": BUILTIN_DATASETS}
        registry_path = settings.MODELS_DIR / "registry.json"
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text(json.dumps(registry_payload, ensure_ascii=False, indent=2), encoding="utf-8")

detector_registry = DetectorRegistry()
