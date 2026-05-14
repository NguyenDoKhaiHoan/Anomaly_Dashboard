"""
Unit tests for FraudStatisticalDetector.
"""
import pytest
import pickle
import tempfile
from pathlib import Path
from app.services.inference.fraud_statistical import FraudStatisticalDetector


class TestFraudStatisticalDetector:
    """Test fraud detection detector."""

    @pytest.fixture
    def mock_bundle(self):
        return {
            "threshold": 350.0,
            "zscore_features": ["amt", "distance", "city_pop"],
            "rolling_window": 50,
            "ema_span": 20,
        }

    @pytest.fixture
    def detector_with_bundle(self, mock_bundle):
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            pickle.dump(mock_bundle, f)
            detector = FraudStatisticalDetector(f.name)
        yield detector
        Path(f.name).unlink(missing_ok=True)

    @pytest.fixture
    def detector_without_bundle(self):
        return FraudStatisticalDetector("/nonexistent/path.pkl")

    @pytest.fixture
    def runtime_state(self):
        return {"stat_windows": {}, "ema_values": {}}

    def test_loads_config_from_bundle(self, detector_with_bundle):
        assert detector_with_bundle.default_threshold == 350.0
        assert detector_with_bundle.zscore_features == ["amt", "distance", "city_pop"]
        assert detector_with_bundle.rolling_window == 50
        assert detector_with_bundle.ema_span == 20

    def test_uses_default_config_without_bundle(self, detector_without_bundle):
        assert detector_without_bundle.default_threshold == 350.0
        assert detector_without_bundle.zscore_features == ["amt", "distance", "city_pop"]

    def test_returns_false_when_features_missing(self, detector_with_bundle, runtime_state):
        result = detector_with_bundle.predict({}, {}, runtime_state)
        assert result.is_anomaly is False
        assert result.anomaly_score == 0.0

    def test_normal_transaction_below_threshold(self, detector_with_bundle, runtime_state):
        for _ in range(10):
            features = {"amt": 100.0, "distance": 10.0, "city_pop": 50000}
            result = detector_with_bundle.predict({}, features, runtime_state)
        assert result.is_anomaly is False
        assert result.anomaly_score >= 0

    def test_high_amount_triggers_zscore_flag(self, detector_with_bundle, runtime_state):
        for _ in range(20):
            detector_with_bundle.predict({}, {"amt": 50.0, "distance": 5.0, "city_pop": 50000}, runtime_state)
        result = detector_with_bundle.predict({}, {"amt": 5000.0, "distance": 5.0, "city_pop": 50000}, runtime_state)
        reasons = list(result.reasons)
        assert "amt_zscore_high" in reasons or "score_far_above_threshold" in reasons or "statistical_threshold_exceeded" in reasons

    def test_threshold_override_applied(self, mock_bundle):
        mock_bundle["threshold"] = 10.0
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            pickle.dump(mock_bundle, f)
            detector = FraudStatisticalDetector(f.name)
        Path(f.name).unlink(missing_ok=True)
        runtime = {"stat_windows": {}, "ema_values": {}}
        result = detector.predict({}, {"amt": 1000.0, "distance": 100.0, "city_pop": 100000}, runtime, threshold_override=5.0)
        assert result.metadata.get("threshold") == 5.0

    def test_runtime_state_accumulates_windows(self, detector_with_bundle):
        runtime = {"stat_windows": {}, "ema_values": {}}
        for i in range(5):
            detector_with_bundle.predict({}, {"amt": float(i * 10), "distance": 5.0, "city_pop": 50000}, runtime)
        window = runtime["stat_windows"]["amt"]
        assert len(window) == 5

    def test_prediction_result_structure(self, detector_with_bundle, runtime_state):
        result = detector_with_bundle.predict({}, {"amt": 100.0, "distance": 10.0, "city_pop": 50000}, runtime_state)
        assert hasattr(result, "is_anomaly")
        assert hasattr(result, "anomaly_score")
        assert hasattr(result, "reasons")
        assert hasattr(result, "metadata")

    def test_stream_type_and_model_key(self, detector_with_bundle):
        assert detector_with_bundle.stream_type == "credit_card"
        assert detector_with_bundle.model_key == "fraud_statistical"
