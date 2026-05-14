from __future__ import annotations
from collections import deque

def _std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean_value = sum(values) / len(values)
    return (sum((value - mean_value) ** 2 for value in values) / len(values)) ** 0.5

def engineer_crypto_features(raw_event: dict, runtime_state: dict) -> dict:
    price = float(raw_event["price"])
    volume = float(raw_event["volume"])
    history: deque = runtime_state.setdefault("price_history", deque(maxlen=20))
    prev_price = history[-1] if history else price
    history.append(price)
    returns = 0.0 if prev_price == 0 else (price - prev_price) / prev_price
    rolling_mean = sum(history) / len(history)
    rolling_std = _std(list(history))
    zscore = 0.0 if rolling_std == 0 else (price - rolling_mean) / rolling_std
    return {
        "price": price,
        "volume": volume,
        "return_1": returns,
        "rolling_mean_20": rolling_mean,
        "rolling_std_20": rolling_std,
        "price_zscore_20": zscore,
    }
