from __future__ import annotations
from collections import deque

class MeanShiftDetector:
    def __init__(self, window_size: int = 50, threshold: float = 2.5):
        self.window_size = window_size
        self.threshold = threshold

    def update(self, runtime_state: dict, value: float) -> bool:
        window: deque = runtime_state.setdefault("drift_window", deque(maxlen=self.window_size))
        if len(window) < self.window_size:
            window.append(value)
            return False
        mean_value = sum(window) / len(window)
        std_value = (sum((item - mean_value) ** 2 for item in window) / len(window)) ** 0.5
        shifted = std_value > 0 and abs(value - mean_value) / std_value >= self.threshold
        window.append(value)
        return shifted
