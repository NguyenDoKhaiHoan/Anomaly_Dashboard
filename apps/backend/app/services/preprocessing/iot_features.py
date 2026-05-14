from __future__ import annotations
from collections import deque

# Features expected by IoT LSTM model (must match training)
LSTM_IOT_FEATURES = [
    "Temperature", "Humidity", "Battery_Level",
    "temp_diff", "hum_diff", "bat_diff",
    "temp_mean10", "temp_std10", "hum_mean10", "hum_std10",
]

DEFAULT_IOT_FEATURES = LSTM_IOT_FEATURES

def _std(values: list[float]) -> float:
    if not values:
        return 0.0
    mean_value = sum(values) / len(values)
    return (sum((value - mean_value) ** 2 for value in values) / len(values)) ** 0.5

def engineer_iot_features(raw_event: dict, runtime_state: dict, feature_names: list[str] | None = None) -> dict:
    """Engineer features for IoT sensor data.
    
    Args:
        raw_event: Raw sensor data from IoT device
        runtime_state: Runtime state for maintaining history windows
        feature_names: List of feature names the model expects
        
    Returns:
        Dictionary of engineered features
    """
    feature_names = feature_names or DEFAULT_IOT_FEATURES
    
    # Extract sensor values with safe defaults
    temp = float(raw_event.get("Temperature", 0.0))
    hum = float(raw_event.get("Humidity", 0.0))
    battery = float(raw_event.get("Battery_Level", 0.0))
    
    # Initialize history deques if not exist
    history_temp: deque = runtime_state.setdefault("temp_history", deque(maxlen=10))
    history_hum: deque = runtime_state.setdefault("hum_history", deque(maxlen=10))
    history_bat: deque = runtime_state.setdefault("bat_history", deque(maxlen=10))
    
    # Get previous values
    prev_temp = history_temp[-1] if history_temp else temp
    prev_hum = history_hum[-1] if history_hum else hum
    prev_bat = history_bat[-1] if history_bat else battery
    
    # Append current values to history
    history_temp.append(temp)
    history_hum.append(hum)
    history_bat.append(battery)
    
    # Calculate engineered features
    values = {
        "Temperature": temp,
        "Humidity": hum,
        "Battery_Level": battery,
        # Difference from previous reading
        "temp_diff": temp - prev_temp,
        "hum_diff": hum - prev_hum,
        "bat_diff": battery - prev_bat,
        # Rolling statistics
        "temp_mean10": sum(history_temp) / len(history_temp) if history_temp else temp,
        "temp_std10": _std(list(history_temp)),
        "hum_mean10": sum(history_hum) / len(history_hum) if history_hum else hum,
        "hum_std10": _std(list(history_hum)),
    }
    
    # Return only features that the model expects
    return {name: float(values.get(name, 0.0)) for name in feature_names if name in values}
