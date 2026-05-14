from __future__ import annotations
from app.db_models.alert_rule import AlertRule

def evaluate_rule(rule: AlertRule, event: dict, runtime_state: dict) -> bool:
    if not rule.is_enabled:
        return False
    # Check stream type filter
    stream_type = event.get("stream_type")
    if rule.stream_type and rule.stream_type != stream_type:
        return False
    # Check asset symbol filter (if applicable)
    asset_symbol = event.get("raw_event", {}).get("Device_ID") or event.get("raw_event", {}).get("symbol")
    if rule.asset_symbol and rule.asset_symbol != asset_symbol:
        return False
    # Get score and check threshold
    score = float(event.get("anomaly_score", 0))
    score_ok = score >= float(rule.score_threshold)
    # Track consecutive anomalies
    streak_key = f"rule_streak_{rule.id}"
    previous = int(runtime_state.get(streak_key, 0))
    is_anomaly = event.get("is_anomaly", False)
    if is_anomaly and score_ok:
        runtime_state[streak_key] = previous + 1
    else:
        runtime_state[streak_key] = 0
    return runtime_state[streak_key] >= int(rule.consecutive_count)
