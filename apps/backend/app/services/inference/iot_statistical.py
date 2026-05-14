from __future__ import annotations
from collections import deque
from pathlib import Path
from app.services.inference.base import BaseDetector, PredictionResult

class IoTStatisticalDetector(BaseDetector):
    """
    Statistical anomaly detector for IoT sensor data.
    Uses Z-score and deviation detection when LSTM model is not available.
    """
    stream_type = "iot_sensor"
    model_key = "iot_statistical"
    
    def __init__(self, artifact_path: str | Path | None = None):
        self.artifact_path = Path(artifact_path) if artifact_path else None
        self.default_threshold = 0.65  # Default threshold for IoT statistical detector
        self.threshold = self.default_threshold
        self.window_size = 30
        self.alpha = 0.2  # EMA smoothing factor
        
    def predict(self, raw_event, features, runtime_state, threshold_override=None):
        """
        Predict anomaly using statistical methods:
        - Z-score based on rolling window
        - Sudden change detection
        - Deviation from EMA
        """
        reasons = []
        score = 0.0
        
        # Get feature values
        temp = float(features.get("Temperature", 0.0))
        hum = float(features.get("Humidity", 0.0))
        battery = float(features.get("Battery_Level", 0.0))
        
        # Initialize rolling windows if not exists
        windows = runtime_state.setdefault("stat_windows", {
            "temp": deque(maxlen=self.window_size),
            "hum": deque(maxlen=self.window_size),
            "battery": deque(maxlen=self.window_size),
        })
        
        # Initialize EMA values if not exists
        emas = runtime_state.setdefault("ema_values", {
            "temp": temp,
            "hum": hum,
            "battery": battery,
        })
        
        # Calculate z-scores for each feature
        zscore_total = 0.0
        feature_count = 0
        
        for name, value, history in [
            ("Temperature", temp, windows["temp"]),
            ("Humidity", hum, windows["hum"]),
            ("Battery_Level", battery, windows["battery"]),
        ]:
            # Update EMA
            prev_ema = emas[name]
            new_ema = self.alpha * value + (1 - self.alpha) * prev_ema
            emas[name] = new_ema
            
            # Calculate z-score if we have enough data
            if len(history) >= 5:
                mean_val = sum(history) / len(history)
                variance = sum((v - mean_val) ** 2 for v in history) / len(history)
                std_val = variance ** 0.5
                
                if std_val > 0:
                    zscore = abs((value - mean_val) / std_val)
                    zscore_total += zscore
                    feature_count += 1
                    
                    # Flag anomalies based on z-score
                    if zscore >= 3.0:
                        reasons.append(f"{name}_zscore_high")
                    elif zscore >= 2.0:
                        reasons.append(f"{name}_zscore_elevated")
            
            # Add to rolling window
            history.append(value)
        
        # Normalize score
        if feature_count > 0:
            score = min(zscore_total / feature_count, 1.0)
        
        # Detect sudden changes
        if len(windows["temp"]) >= 2:
            temp_diff = abs(temp - windows["temp"][-1])
            if temp_diff > 3.0:
                reasons.append("temp_sudden_change")
                score = max(score, 0.7)
        
        if len(windows["hum"]) >= 2:
            hum_diff = abs(hum - windows["hum"][-1])
            if hum_diff > 5.0:
                reasons.append("humidity_sudden_change")
                score = max(score, 0.7)
        
        # Battery anomaly detection (rapid drain or abnormal levels)
        if battery < 10:
            reasons.append("battery_low")
            score = max(score, 0.8)
        
        # Determine threshold
        threshold = threshold_override if threshold_override is not None else self.threshold
        is_anomaly = score >= threshold
        
        # Add reason if score is significantly above threshold
        if score >= threshold * 1.3 and not reasons:
            reasons.append("statistical_threshold_exceeded")
        
        # Add metadata
        metadata = {
            "threshold": threshold,
            "method": "statistical_zscore",
            "features_analyzed": feature_count,
        }
        
        return PredictionResult(
            is_anomaly=is_anomaly,
            anomaly_score=score,
            reasons=reasons if reasons else [],
            metadata=metadata
        )
