from __future__ import annotations

import math
from typing import Any
import pandas as pd

CATEGORICAL_COLUMNS = ["merchant", "category", "gender", "state", "job"]

def encode_value(column: str, value: Any, label_maps: dict[str, dict[str, int]]) -> int:
    string_value = str(value)
    mapping = label_maps.setdefault(column, {})
    if string_value not in mapping:
        mapping[string_value] = len(mapping)
    return mapping[string_value]

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c

def engineer_fraud_features(raw_event: dict[str, Any], runtime_state: dict[str, Any]) -> dict[str, Any]:
    """Engineer features for fraud detection.
    
    Returns RAW values - the server will compute rolling z-scores internally.
    This matches the training notebook approach.
    """
    label_maps = runtime_state.setdefault("label_maps", {column: {} for column in CATEGORICAL_COLUMNS})
    trans_dt = pd.to_datetime(raw_event["trans_date_trans_time"])
    dob_dt = pd.to_datetime(raw_event["dob"])
    age = trans_dt.year - dob_dt.year - ((trans_dt.month, trans_dt.day) < (dob_dt.month, dob_dt.day))
    distance_km = haversine_km(
        float(raw_event["lat"]),
        float(raw_event["long"]),
        float(raw_event["merch_lat"]),
        float(raw_event["merch_long"]),
    )
    distance_miles = distance_km * 0.621371  # Convert km to miles (match training data)
    
    return {
        # Raw values - server will compute z-scores with global stats
        "amt": float(raw_event["amt"]),
        "city_pop": float(raw_event["city_pop"]),
        "distance": float(distance_miles),
        # Other features
        "card_holder_age": float(age),
        "trans_hour": int(trans_dt.hour),
        "trans_weekday": int(trans_dt.weekday()),
        "trans_month": int(trans_dt.month),
        "merchant": int(encode_value("merchant", raw_event["merchant"], label_maps)),
        "category": int(encode_value("category", raw_event["category"], label_maps)),
        "gender": int(encode_value("gender", raw_event["gender"], label_maps)),
        "state": int(encode_value("state", raw_event["state"], label_maps)),
        "job": int(encode_value("job", raw_event["job"], label_maps)),
    }
