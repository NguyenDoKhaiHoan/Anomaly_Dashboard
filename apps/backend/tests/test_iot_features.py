"""
Unit tests for IoT feature engineering module.
"""
import pytest
from collections import deque
from app.services.preprocessing.iot_features import (
    engineer_iot_features,
    _std,
    DEFAULT_IOT_FEATURES,
    LSTM_IOT_FEATURES,
)


class TestStd:
    """Test standard deviation calculation."""

    def test_empty_list_returns_zero(self):
        assert _std([]) == pytest.approx(0.0)

    def test_single_value_returns_zero(self):
        assert _std([5.0]) == pytest.approx(0.0)

    def test_constant_values_returns_zero(self):
        assert _std([5.0, 5.0, 5.0, 5.0]) == pytest.approx(0.0)

    def test_known_values(self):
        values = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        std = _std(values)
        assert std == pytest.approx(2.0, abs=0.001)


class TestEngineerIoTFeatures:
    """Test IoT feature engineering pipeline."""

    @pytest.fixture
    def runtime_state(self):
        return {}

    @pytest.fixture
    def sample_raw_event(self):
        return {
            "Temperature": 25.5,
            "Humidity": 60.0,
            "Battery_Level": 85.0,
        }

    def test_returns_all_required_features(self, runtime_state, sample_raw_event):
        features = engineer_iot_features(sample_raw_event, runtime_state)
        for feat in DEFAULT_IOT_FEATURES:
            assert feat in features, f"Missing feature: {feat}"

    def test_raw_features_preserved(self, runtime_state, sample_raw_event):
        features = engineer_iot_features(sample_raw_event, runtime_state)
        assert features["Temperature"] == pytest.approx(25.5)
        assert features["Humidity"] == pytest.approx(60.0)
        assert features["Battery_Level"] == pytest.approx(85.0)

    def test_diff_features_zero_on_first_event(self, runtime_state, sample_raw_event):
        features = engineer_iot_features(sample_raw_event, runtime_state)
        assert features["temp_diff"] == pytest.approx(0.0)
        assert features["hum_diff"] == pytest.approx(0.0)
        assert features["bat_diff"] == pytest.approx(0.0)

    def test_diff_features_calculated_correctly(self, runtime_state):
        event1 = {"Temperature": 25.0, "Humidity": 60.0, "Battery_Level": 80.0}
        event2 = {"Temperature": 27.0, "Humidity": 58.0, "Battery_Level": 79.0}
        f1 = engineer_iot_features(event1, runtime_state)
        f2 = engineer_iot_features(event2, runtime_state)
        assert f2["temp_diff"] == pytest.approx(2.0)
        assert f2["hum_diff"] == pytest.approx(-2.0)
        assert f2["bat_diff"] == pytest.approx(-1.0)

    def test_mean_features_equal_to_value_on_first_event(self, runtime_state, sample_raw_event):
        features = engineer_iot_features(sample_raw_event, runtime_state)
        assert features["temp_mean10"] == pytest.approx(25.5)
        assert features["hum_mean10"] == pytest.approx(60.0)

    def test_mean_features_accumulate_over_multiple_events(self, runtime_state):
        temps = [20.0, 22.0, 24.0, 26.0, 28.0]
        hums = [50.0, 52.0, 54.0, 56.0, 58.0]
        expected_mean_temp = sum(temps) / len(temps)
        expected_mean_hum = sum(hums) / len(hums)
        for t, h in zip(temps, hums):
            engineer_iot_features({"Temperature": t, "Humidity": h, "Battery_Level": 100.0}, runtime_state)
        features = engineer_iot_features({"Temperature": 30.0, "Humidity": 60.0, "Battery_Level": 100.0}, runtime_state)
        assert features["temp_mean10"] == pytest.approx(expected_mean_temp, abs=0.001)
        assert features["hum_mean10"] == pytest.approx(expected_mean_hum, abs=0.001)

    def test_std_features_zero_on_single_value(self, runtime_state, sample_raw_event):
        features = engineer_iot_features(sample_raw_event, runtime_state)
        assert features["temp_std10"] == pytest.approx(0.0)
        assert features["hum_std10"] == pytest.approx(0.0)

    def test_std_features_nonzero_on_varying_values(self, runtime_state):
        for t in [20.0, 25.0, 30.0]:
            engineer_iot_features({"Temperature": t, "Humidity": 50.0, "Battery_Level": 100.0}, runtime_state)
        features = engineer_iot_features({"Temperature": 35.0, "Humidity": 50.0, "Battery_Level": 100.0}, runtime_state)
        assert features["temp_std10"] > 0

    def test_history_deques_maintained_in_runtime_state(self, runtime_state):
        event = {"Temperature": 25.0, "Humidity": 60.0, "Battery_Level": 80.0}
        engineer_iot_features(event, runtime_state)
        assert "temp_history" in runtime_state
        assert "hum_history" in runtime_state
        assert "bat_history" in runtime_state
        assert isinstance(runtime_state["temp_history"], deque)
        assert len(runtime_state["temp_history"]) == 1

    def test_history_window_limited_to_10(self, runtime_state):
        for i in range(15):
            engineer_iot_features(
                {"Temperature": float(i), "Humidity": 50.0, "Battery_Level": 100.0},
                runtime_state
            )
        assert len(runtime_state["temp_history"]) == 10

    def test_filter_by_feature_names(self, runtime_state):
        event = {"Temperature": 25.0, "Humidity": 60.0, "Battery_Level": 80.0}
        features = engineer_iot_features(event, runtime_state, feature_names=["Temperature", "Humidity"])
        assert "Temperature" in features
        assert "Humidity" in features
        assert "Battery_Level" not in features
