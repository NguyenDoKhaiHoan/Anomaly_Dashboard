from __future__ import annotations
from app.services.drift.detector import MeanShiftDetector

class DriftMonitor:
    def __init__(self):
        self.detector = MeanShiftDetector()
    def check(self, runtime_state: dict, score: float) -> bool:
        return self.detector.update(runtime_state, score)

drift_monitor = DriftMonitor()
