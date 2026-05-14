"""
Unit tests for fraud feature engineering module.
"""
import pytest
from collections import deque
from app.services.preprocessing.fraud_features import (
    engineer_fraud_features,
    haversine_km,
    encode_value,
    CATEGORICAL_COLUMNS,
)


class TestHaversineDistance:
    """Test haversine distance calculation."""

    def test_same_location_returns_zero(self):
        assert haversine_km(40.7128, -74.0060, 40.7128, -74.0060) == pytest.approx(0.0, abs=0.001)

    def test_known_distance_nyc_to_la(self):
        nyc_lat, nyc_lon = 40.7128, -74.0060
        la_lat, la_lon = 34.0522, -118.2437
        distance = haversine_km(nyc_lat, nyc_lon, la_lat, la_lon)
        assert 3900 < distance < 4000

    def test_symmetry(self):
        lat1, lon1 = 34.05, -118.24
        lat2, lon2 = 34.10, -118.20
        assert haversine_km(lat1, lon1, lat2, lon2) == pytest.approx(
            haversine_km(lat2, lon2, lat1, lon1), rel=1e-9
        )


class TestEncodeValue:
    """Test categorical encoding."""

    def test_first_value_gets_zero(self):
        label_maps = {}
        result = encode_value("merchant", "amazon", label_maps)
        assert result == 0

    def test_same_value_returns_same_code(self):
        label_maps = {"merchant": {"amazon": 0}}
        result = encode_value("merchant", "amazon", label_maps)
        assert result == 0

    def test_different_values_get_incremental_codes(self):
        label_maps = {"merchant": {"amazon": 0}}
        result = encode_value("merchant", "walmart", label_maps)
        assert result == 1


class TestEngineerFraudFeatures:
    """Test fraud feature engineering pipeline."""

    @pytest.fixture
    def runtime_state(self):
        return {"label_maps": {col: {} for col in CATEGORICAL_COLUMNS}}

    @pytest.fixture
    def sample_raw_event(self):
        return {
            "trans_date_trans_time": "2026-05-09 08:00:00",
            "merchant": "amazon",
            "category": "shopping_net",
            "amt": 120.5,
            "gender": "F",
            "state": "CA",
            "city_pop": 300000,
            "job": "Engineer",
            "dob": "1996-08-11",
            "lat": 34.05,
            "long": -118.24,
            "merch_lat": 34.10,
            "merch_long": -118.20,
        }

    def test_returns_required_numeric_features(self, runtime_state, sample_raw_event):
        features = engineer_fraud_features(sample_raw_event, runtime_state)
        assert "amt" in features
        assert "city_pop" in features
        assert "distance" in features
        assert "card_holder_age" in features

    def test_calculates_distance_correctly(self, runtime_state, sample_raw_event):
        features = engineer_fraud_features(sample_raw_event, runtime_state)
        assert "distance" in features
        assert isinstance(features["distance"], float)
        assert features["distance"] >= 0

    def test_raw_features_match_input(self, runtime_state, sample_raw_event):
        """Test that features match original input values."""
        features = engineer_fraud_features(sample_raw_event, runtime_state)
        assert features["amt"] == sample_raw_event["amt"]
        assert features["city_pop"] == sample_raw_event["city_pop"]
        assert features["distance"] == features["distance"]  # Raw distance value

    def test_calculates_age_correctly(self, runtime_state, sample_raw_event):
        features = engineer_fraud_features(sample_raw_event, runtime_state)
        age = features["card_holder_age"]
        trans_year = 2026
        dob_year = 1996
        expected_age = trans_year - dob_year
        assert abs(age - expected_age) <= 1

    def test_extracts_temporal_features(self, runtime_state, sample_raw_event):
        features = engineer_fraud_features(sample_raw_event, runtime_state)
        assert "trans_hour" in features
        assert "trans_weekday" in features
        assert "trans_month" in features
        assert features["trans_hour"] == 8
        assert features["trans_month"] == 5

    def test_encodes_categorical_features(self, runtime_state, sample_raw_event):
        features = engineer_fraud_features(sample_raw_event, runtime_state)
        assert "merchant" in features
        assert "category" in features
        assert "gender" in features
        assert "state" in features
        assert "job" in features

    def test_consistent_encoding_across_calls(self, runtime_state, sample_raw_event):
        engineer_fraud_features(sample_raw_event, runtime_state)
        second_event = sample_raw_event.copy()
        second_event["amt"] = 200.0
        features2 = engineer_fraud_features(second_event, runtime_state)
        assert features2["merchant"] == 0
        assert features2["category"] == 0

    def test_maintains_separate_label_maps_per_column(self, runtime_state):
        event1 = {
            "trans_date_trans_time": "2026-05-09 08:00:00",
            "merchant": "amazon",
            "category": "shopping",
            "amt": 100.0,
            "gender": "F",
            "state": "CA",
            "city_pop": 100000,
            "job": "Engineer",
            "dob": "1990-01-01",
            "lat": 34.05,
            "long": -118.24,
            "merch_lat": 34.10,
            "merch_long": -118.20,
        }
        event2 = {
            "trans_date_trans_time": "2026-05-09 09:00:00",
            "merchant": "walmart",
            "category": "grocery",
            "amt": 50.0,
            "gender": "M",
            "state": "TX",
            "city_pop": 200000,
            "job": "Teacher",
            "dob": "1985-05-15",
            "lat": 29.76,
            "long": -95.36,
            "merch_lat": 29.75,
            "merch_long": -95.42,
        }
        f1 = engineer_fraud_features(event1, runtime_state)
        f2 = engineer_fraud_features(event2, runtime_state)
        assert f1["merchant"] == 0
        assert f2["merchant"] == 1
        assert f1["category"] == 0
        assert f2["category"] == 1
