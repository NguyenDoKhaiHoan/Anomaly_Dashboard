from __future__ import annotations
import pickle
import json
from collections import deque
from pathlib import Path
from app.services.inference.base import BaseDetector, PredictionResult
from app.core.logging import logger


class FraudStatisticalDetector(BaseDetector):
    stream_type = "credit_card"
    model_key = "fraud_statistical"

    def __init__(self, artifact_path: str | Path):
        self.artifact_path = Path(artifact_path)
        self.bundle = {}
        if self.artifact_path.exists():
            suffix = self.artifact_path.suffix.lower()
            if suffix == ".json":
                with self.artifact_path.open("r", encoding="utf-8") as f:
                    self.bundle = json.load(f)
            else:
                with self.artifact_path.open("rb") as f:
                    self.bundle = pickle.load(f)
        
        # Load config from bundle
        self.default_threshold = float(self.bundle.get("threshold", 14.27))
        self.zscore_features = list(self.bundle.get("zscore_features", ["amt", "distance"]))
        self.extra_features = list(self.bundle.get("extra_features", ["city_pop", "ema_diff"]))
        self.rolling_window = int(self.bundle.get("rolling_window", 50))
        self.ema_span = int(self.bundle.get("ema_span", 20))
        self.alpha = 2.0 / (self.ema_span + 1.0)
        self.best_f1 = float(self.bundle.get("best_f1", 0.378))
        
        # Load weights
        best_weights = self.bundle.get("best_weights", (0.5, 0.5, 0.5, 3.0))
        if isinstance(best_weights, (list, tuple)):
            self.zscore_weight = float(best_weights[0])
            self.city_weight = float(best_weights[1])
            self.ema_diff_weight = float(best_weights[2])
            self.ema_gap_mult = float(best_weights[3])
        else:
            self.zscore_weight = float(best_weights.get("zscore_weight", 0.5))
            self.city_weight = float(best_weights.get("city_pop_weight", 0.5))
            self.ema_diff_weight = float(best_weights.get("ema_diff_weight", 0.5))
            self.ema_gap_mult = float(best_weights.get("ema_gap_multiplier", 3.0))
        
        # Load GLOBAL statistical params (from training) for z-score calculation
        self.global_mean = self.bundle.get("global_mean", {})
        self.global_std = self.bundle.get("global_std", {})
        
        # Fallback to statistical_params if available
        stat_params = self.bundle.get("statistical_params", {})
        
        # Fallback values if not in bundle
        if "amt" not in self.global_mean:
            self.global_mean["amt"] = 70.35
        if "amt" not in self.global_std:
            self.global_std["amt"] = 160.32
        if "distance" not in self.global_mean:
            self.global_mean["distance"] = 47.47
        if "distance" not in self.global_std:
            self.global_std["distance"] = 18.07
        
        # City pop global stats
        city_params = stat_params.get("city_pop", {})
        self.city_mu = float(city_params.get("mu", 88824.44))
        self.city_sd = float(city_params.get("sd", 301956.36))
        
        # EMA diff global stats
        ema_params = stat_params.get("ema_diff", {})
        self.ema_mu = float(ema_params.get("mu", 60.92))
        self.ema_sd = float(ema_params.get("sd", 153.92))
        
        logger.info(f"[FraudDetector] Loaded: threshold={self.default_threshold}, "
                   f"zscore_weight={self.zscore_weight}, city_weight={self.city_weight}, "
                   f"ema_diff_weight={self.ema_diff_weight}, ema_gap_mult={self.ema_gap_mult}, "
                   f"global_mean={self.global_mean}")

    def predict(self, raw_event, features, runtime_state, threshold_override=None):
        reasons = []
        
        raw_amt = float(features.get("amt", 0.0))
        raw_distance = float(features.get("distance", 0.0))
        raw_city_pop = float(features.get("city_pop", 0.0))
        
        # Z-SCORE với GLOBAL STATISTICS
        amt_mean = self.global_mean.get("amt", 70.35)
        amt_std = self.global_std.get("amt", 160.32)
        amt_zscore = abs(raw_amt - amt_mean) / (amt_std + 1e-10)
        if amt_zscore >= 3.0:
            reasons.append("amt_zscore_high")
        
        dist_mean = self.global_mean.get("distance", 0.77)
        dist_std = self.global_std.get("distance", 0.28)
        dist_zscore = abs(raw_distance - dist_mean) / (dist_std + 1e-10)
        
        city_zscore = abs(raw_city_pop - self.city_mu) / (self.city_sd + 1e-10)
        
        # EMA cho temporal tracking
        ema_map = runtime_state.setdefault("ema_values", {})
        
        prev_ema_amt = ema_map.get("amt", raw_amt)
        new_ema_amt = self.alpha * raw_amt + (1.0 - self.alpha) * prev_ema_amt
        ema_map["amt"] = new_ema_amt
        
        prev_ema_dist = ema_map.get("distance", raw_distance)
        new_ema_dist = self.alpha * raw_distance + (1.0 - self.alpha) * prev_ema_dist
        ema_map["distance"] = new_ema_dist
        
        ema_gap = abs(raw_amt - new_ema_amt) + abs(raw_distance - new_ema_dist)
        ema_gap_zscore = abs(ema_gap - self.ema_mu) / (self.ema_sd + 1e-10)
        
        # SCORE = (amt_z + dist_z) * zscore_weight + city_z * city_weight + ema_gap_z * (ema_diff_weight + ema_gap_mult)
        score = (
            (amt_zscore + dist_zscore) * self.zscore_weight +
            city_zscore * self.city_weight +
            ema_gap_zscore * (self.ema_diff_weight + self.ema_gap_mult)
        )
        
        threshold = threshold_override if threshold_override is not None else self.default_threshold
        is_anomaly = score >= threshold
        
        if score >= threshold * 1.2:
            reasons.append("score_far_above_threshold")
        if not reasons and is_anomaly:
            reasons.append("statistical_threshold_exceeded")
        
        return PredictionResult(
            is_anomaly=is_anomaly, 
            anomaly_score=float(score), 
            reasons=reasons if reasons else [], 
            metadata={
                "threshold": threshold,
                "zscore": {
                    "amt": amt_zscore,
                    "distance": dist_zscore,
                    "city_pop": city_zscore,
                    "ema_gap": ema_gap_zscore
                },
                "score_contrib": {
                    "zscore_amt": amt_zscore * self.zscore_weight,
                    "zscore_dist": dist_zscore * self.zscore_weight,
                    "city": city_zscore * self.city_weight,
                    "ema_gap": ema_gap_zscore * (self.ema_diff_weight + self.ema_gap_mult)
                },
                "weights": {
                    "zscore": self.zscore_weight,
                    "city": self.city_weight,
                    "ema_diff": self.ema_diff_weight,
                    "ema_gap_mult": self.ema_gap_mult
                }
            }
        )
