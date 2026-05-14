from __future__ import annotations
from collections import deque
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from app.services.inference.base import BaseDetector, PredictionResult

class SequenceLSTMClassifier(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 256, num_layers: int = 3):
        super().__init__()
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, sequence: torch.Tensor) -> torch.Tensor:
        output, _ = self.lstm(sequence)
        return self.fc(output[:, -1, :])

class IoTLSTMDetector(BaseDetector):
    stream_type = "iot_sensor"
    model_key = "iot_lstm"

    def __init__(self, artifact_path: str | Path):
        self.artifact_path = Path(artifact_path)
        self.model = None
        self.scaler = None
        self.default_threshold = 0.45
        self.threshold = 0.45
        self.window_size = 80
        self.feature_names = []
        self.loaded = False
        self._load()

    def _load(self) -> None:
        if not self.artifact_path.exists():
            return
        bundle = torch.load(self.artifact_path, map_location="cpu", weights_only=False)
        self.scaler = bundle.get("scaler")
        self.threshold = float(bundle.get("threshold", 0.45))
        self.window_size = int(bundle.get("window_size", 80))
        self.feature_names = list(bundle.get("features", []))
        state_dict = bundle.get("model_state_dict", {})
        input_size = len(self.feature_names)
        hidden_size = state_dict["fc.weight"].shape[1]
        num_layers = len([name for name in state_dict.keys() if name.startswith("lstm.weight_ih_")])
        model = SequenceLSTMClassifier(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers)
        model.load_state_dict(state_dict)
        model.eval()
        self.model = model
        self.loaded = True

    def predict(self, raw_event, features, runtime_state, threshold_override=None):
        if not self.loaded or self.model is None or self.scaler is None:
            return PredictionResult(False, 0.0, ["model_not_loaded"])
        feature_vector = [float(features[name]) for name in self.feature_names]
        sequence_buffer: deque = runtime_state.setdefault("sequence_buffer", deque(maxlen=self.window_size))
        sequence_buffer.append(feature_vector)
        if len(sequence_buffer) < self.window_size:
            return PredictionResult(False, 0.0, ["warming_up_window"], {"window_progress": len(sequence_buffer), "window_size": self.window_size})
        sequence = np.array(sequence_buffer, dtype=np.float32)
        # Use DataFrame to preserve feature names for sklearn scaler
        df = pd.DataFrame(sequence, columns=self.feature_names)
        scaled = self.scaler.transform(df)
        tensor = torch.tensor(scaled, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            logit = self.model(tensor)
            probability = float(torch.sigmoid(logit).item())
        threshold = threshold_override if threshold_override is not None else self.threshold
        is_anomaly = probability >= threshold
        reasons = ["iot_sequence_probability_high"] if is_anomaly else []
        return PredictionResult(is_anomaly=is_anomaly, anomaly_score=probability, reasons=reasons, metadata={"threshold": threshold, "window_size": self.window_size})
