"""
Unit tests for IoTLSTMDetector.
"""
import pytest
import torch
import tempfile
from pathlib import Path
from collections import deque
import numpy as np
from app.services.inference.iot_lstm import IoTLSTMDetector, SequenceLSTMClassifier


class TestSequenceLSTMClassifier:
    """Test LSTM model architecture."""

    def test_forward_pass_returns_correct_shape(self):
        model = SequenceLSTMClassifier(input_size=10, hidden_size=64, num_layers=2)
        batch_size = 2
        seq_len = 50
        input_size = 10
        dummy_input = torch.randn(batch_size, seq_len, input_size)
        output = model(dummy_input)
        assert output.shape == (batch_size, 1)

    def test_model_can_be_eval_mode(self):
        model = SequenceLSTMClassifier(input_size=5, hidden_size=32, num_layers=1)
        model.eval()
        dummy_input = torch.randn(1, 20, 5)
        with torch.no_grad():
            output = model(dummy_input)
        assert output.shape == (1, 1)


class TestIoTLSTMDetector:
    """Test IoT LSTM detector."""

    @pytest.fixture
    def mock_bundle(self):
        input_size = 10
        hidden_size = 64
        num_layers = 2
        model = SequenceLSTMClassifier(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers)
        scaler_mean = np.zeros(input_size)
        scaler_scale = np.ones(input_size)
        class MockScaler:
            def transform(self, x):
                return (x - scaler_mean) / scaler_scale
        return {
            "model_state_dict": model.state_dict(),
            "scaler": MockScaler(),
            "threshold": 0.45,
            "window_size": 10,
            "features": ["Temperature", "Humidity", "Battery_Level", "temp_diff", "hum_diff", "bat_diff", "temp_mean10", "temp_std10", "hum_mean10", "hum_std10"],
        }

    @pytest.fixture
    def detector_with_bundle(self, mock_bundle):
        with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as f:
            torch.save(mock_bundle, f)
            detector = IoTLSTMDetector(f.name)
        yield detector
        Path(f.name).unlink(missing_ok=True)

    @pytest.fixture
    def detector_without_bundle(self):
        return IoTLSTMDetector("/nonexistent/path.pt")

    @pytest.fixture
    def runtime_state(self):
        return {"sequence_buffer": deque(maxlen=10)}

    def test_loads_config_from_bundle(self, detector_with_bundle):
        assert detector_with_bundle.threshold == 0.45
        assert detector_with_bundle.window_size == 10
        assert len(detector_with_bundle.feature_names) == 10
        assert detector_with_bundle.loaded is True

    def test_not_loaded_without_bundle(self, detector_without_bundle):
        assert detector_without_bundle.loaded is False
        assert detector_without_bundle.model is None

    def test_returns_model_not_loaded_when_unavailable(self, detector_without_bundle, runtime_state):
        features = {name: 0.0 for name in ["Temperature", "Humidity", "Battery_Level", "temp_diff", "hum_diff", "bat_diff", "temp_mean10", "temp_std10", "hum_mean10", "hum_std10"]}
        result = detector_without_bundle.predict({}, features, runtime_state)
        assert result.is_anomaly is False
        assert "model_not_loaded" in result.reasons

    def test_warming_up_during_buffer_fill(self, detector_with_bundle, runtime_state):
        runtime_state["sequence_buffer"] = deque(maxlen=10)
        features = {name: 25.0 for name in detector_with_bundle.feature_names}
        for _ in range(5):
            result = detector_with_bundle.predict({}, features, runtime_state)
        assert result.is_anomaly is False
        assert "warming_up_window" in result.reasons
        assert result.metadata.get("window_progress") == 5

    def test_prediction_after_window_filled(self, detector_with_bundle, runtime_state):
        runtime_state["sequence_buffer"] = deque(maxlen=10)
        features = {name: 25.0 for name in detector_with_bundle.feature_names}
        for _ in range(10):
            result = detector_with_bundle.predict({}, features, runtime_state)
        assert result.anomaly_score >= 0.0
        assert result.anomaly_score <= 1.0

    def test_anomaly_score_in_valid_range(self, detector_with_bundle, runtime_state):
        runtime_state["sequence_buffer"] = deque(maxlen=10)
        features = {name: float(i % 3) + 20.0 for i, name in enumerate(detector_with_bundle.feature_names)}
        for _ in range(10):
            result = detector_with_bundle.predict({}, features, runtime_state)
        assert 0.0 <= result.anomaly_score <= 1.0

    def test_threshold_override_applied(self, mock_bundle):
        mock_bundle["threshold"] = 0.9
        with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as f:
            torch.save(mock_bundle, f)
            detector = IoTLSTMDetector(f.name)
        Path(f.name).unlink(missing_ok=True)
        runtime = {"sequence_buffer": deque(maxlen=10)}
        features = {name: 25.0 for name in detector.feature_names}
        for _ in range(10):
            result = detector.predict({}, features, runtime, threshold_override=0.99)
        assert result.metadata.get("threshold") == 0.99

    def test_prediction_result_structure(self, detector_with_bundle, runtime_state):
        features = {name: 25.0 for name in detector_with_bundle.feature_names}
        for _ in range(10):
            result = detector_with_bundle.predict({}, features, runtime_state)
        assert hasattr(result, "is_anomaly")
        assert hasattr(result, "anomaly_score")
        assert hasattr(result, "reasons")
        assert hasattr(result, "metadata")

    def test_stream_type_and_model_key(self, detector_with_bundle):
        assert detector_with_bundle.stream_type == "iot_sensor"
        assert detector_with_bundle.model_key == "iot_lstm"

    def test_sequence_buffer_appended_per_predict(self, detector_with_bundle, runtime_state):
        runtime_state["sequence_buffer"] = deque(maxlen=10)
        features = {name: 25.0 for name in detector_with_bundle.feature_names}
        initial_len = len(runtime_state["sequence_buffer"])
        detector_with_bundle.predict({}, features, runtime_state)
        assert len(runtime_state["sequence_buffer"]) == initial_len + 1
