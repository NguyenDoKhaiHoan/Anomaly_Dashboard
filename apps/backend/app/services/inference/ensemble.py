from __future__ import annotations
from statistics import mean
from app.services.inference.base import BaseDetector, PredictionResult

class AverageScoreEnsemble(BaseDetector):
    stream_type = "hybrid"
    model_key = "ensemble_average"
    def __init__(self, detectors: list[BaseDetector]):
        self.detectors = detectors

    def predict(self, raw_event, features, runtime_state, threshold_override=None):
        results = [detector.predict(raw_event, features, runtime_state.setdefault(detector.model_key, {}), threshold_override) for detector in self.detectors]
        average_score = mean([result.anomaly_score for result in results]) if results else 0.0
        is_anomaly = any(result.is_anomaly for result in results)
        reasons = [reason for result in results for reason in result.reasons]
        return PredictionResult(is_anomaly=is_anomaly, anomaly_score=average_score, reasons=reasons)
