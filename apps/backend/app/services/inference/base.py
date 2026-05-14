from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

@dataclass
class PredictionResult:
    is_anomaly: bool
    anomaly_score: float
    reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

class BaseDetector(ABC):
    stream_type: str
    model_key: str

    @abstractmethod
    def predict(self, raw_event: dict[str, Any], features: dict[str, Any], runtime_state: dict[str, Any], threshold_override: float | None = None) -> PredictionResult:
        raise NotImplementedError
