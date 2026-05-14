"""
Unit tests for SessionManager.
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch
from app.services.stream.session_manager import SessionManager, RuntimeSession
from app.db_models.stream_session import StreamSession


class TestRuntimeSession:
    """Test RuntimeSession dataclass."""

    def test_default_values(self):
        session = RuntimeSession(
            session_id="test-123",
            user_id=1,
            stream_type="credit_card",
            model_key="fraud_statistical",
        )
        assert session.session_id == "test-123"
        assert session.user_id == 1
        assert session.stream_type == "credit_card"
        assert session.model_key == "fraud_statistical"
        assert session.running is False
        assert session.status == "created"
        assert isinstance(session.queue, asyncio.Queue)
        assert isinstance(session.counters, dict)

    def test_custom_values(self):
        session = RuntimeSession(
            session_id="custom-456",
            user_id=2,
            stream_type="iot_sensor",
            model_key="iot_lstm",
            stream_interval=2.5,
            threshold_override=0.5,
            status="running",
        )
        assert session.stream_interval == 2.5
        assert session.threshold_override == 0.5
        assert session.status == "running"


class TestSessionManager:
    """Test SessionManager class."""

    @pytest.fixture
    def manager(self):
        return SessionManager()

    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        return db

    def test_initial_state(self, manager):
        assert len(manager.sessions) == 0
        assert manager.active_count() == 0

    def test_register_from_db(self, manager):
        db_session = MagicMock(spec=StreamSession)
        db_session.id = "session-001"
        db_session.user_id = 1
        db_session.stream_type = "credit_card"
        db_session.model_key = "fraud_statistical"
        db_session.dataset_key = "credit_card_10k"
        db_session.asset_symbol = None
        db_session.stream_interval = 1.0
        db_session.threshold_override = None
        db_session.status = "created"

        runtime = manager.register_from_db(db_session)
        assert runtime.session_id == "session-001"
        assert runtime.stream_type == "credit_card"
        assert runtime.model_key == "fraud_statistical"
        assert runtime.session_id in manager.sessions

    def test_update_runtime_interval(self, manager):
        runtime = RuntimeSession(
            session_id="test",
            user_id=1,
            stream_type="credit_card",
            model_key="fraud_statistical",
            stream_interval=1.0,
        )
        manager.update_runtime(runtime, stream_interval=2.5)
        assert runtime.stream_interval == 2.5

    def test_update_runtime_threshold(self, manager):
        runtime = RuntimeSession(
            session_id="test",
            user_id=1,
            stream_type="credit_card",
            model_key="fraud_statistical",
            threshold_override=None,
        )
        manager.update_runtime(runtime, threshold_override=400.0)
        assert runtime.threshold_override == 400.0

    def test_resolve_dataset_path(self, manager, mock_db):
        with patch("app.services.stream.session_manager.DatasetRegistry") as MockDataset:
            mock_dataset = MagicMock()
            mock_dataset.path = "/data/credit.csv"
            mock_db.query.return_value.filter.return_value.first.return_value = mock_dataset
            path = manager._resolve_dataset_path(mock_db, "credit_10k")
            assert path == "/data/credit.csv"

    def test_resolve_dataset_path_none_key(self, manager, mock_db):
        path = manager._resolve_dataset_path(mock_db, None)
        assert path is None

    def test_build_streamer_credit_card(self, manager, mock_db):
        with patch.object(manager, "_resolve_dataset_path", return_value="/path/to/credit.csv"):
            runtime = RuntimeSession(
                session_id="test",
                user_id=1,
                stream_type="credit_card",
                model_key="fraud_statistical",
            )
            streamer = manager._build_streamer(runtime, mock_db)
            from app.services.stream.simulators.credit_stream import CreditCardStream
            assert isinstance(streamer, CreditCardStream)

    def test_build_streamer_iot(self, manager, mock_db):
        with patch.object(manager, "_resolve_dataset_path", return_value="/path/to/iot.csv"):
            runtime = RuntimeSession(
                session_id="test",
                user_id=1,
                stream_type="iot_sensor",
                model_key="iot_lstm",
            )
            streamer = manager._build_streamer(runtime, mock_db)
            from app.services.stream.simulators.iot_stream import IoTSensorStream
            assert isinstance(streamer, IoTSensorStream)

    def test_build_streamer_unsupported_raises(self, manager, mock_db):
        runtime = RuntimeSession(
            session_id="test",
            user_id=1,
            stream_type="unknown_type",
            model_key="unknown_model",
        )
        with pytest.raises(ValueError, match="Unsupported stream_type"):
            manager._build_streamer(runtime, mock_db)

    def test_preprocess_credit_card(self, manager):
        runtime = RuntimeSession(
            session_id="test",
            user_id=1,
            stream_type="credit_card",
            model_key="fraud_statistical",
        )
        raw_event = {
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
        detector = MagicMock()
        detector.feature_names = ["amt", "distance", "city_pop"]
        result = manager._preprocess(runtime, raw_event, detector)
        assert "amt" in result
        assert "distance" in result
        assert "city_pop" in result

    def test_preprocess_iot(self, manager):
        runtime = RuntimeSession(
            session_id="test",
            user_id=1,
            stream_type="iot_sensor",
            model_key="iot_lstm",
        )
        raw_event = {
            "Temperature": 25.0,
            "Humidity": 60.0,
            "Battery_Level": 80.0,
        }
        detector = MagicMock()
        detector.feature_names = ["Temperature", "Humidity", "Battery_Level", "temp_diff", "hum_diff", "bat_diff", "temp_mean10", "temp_std10", "hum_mean10", "hum_std10"]
        result = manager._preprocess(runtime, raw_event, detector)
        assert "Temperature" in result
        assert "temp_diff" in result

    @pytest.mark.asyncio
    async def test_start_already_running(self, manager):
        runtime = RuntimeSession(
            session_id="test",
            user_id=1,
            stream_type="credit_card",
            model_key="fraud_statistical",
            running=True,
        )
        manager.sessions["test"] = runtime
        db_session = MagicMock(spec=StreamSession)
        db_session.id = "test"
        result = await manager.start(db_session, db_session)
        assert result.running is True
        assert result is runtime

    @pytest.mark.asyncio
    async def test_stop_session(self, manager):
        runtime = RuntimeSession(
            session_id="test",
            user_id=1,
            stream_type="credit_card",
            model_key="fraud_statistical",
        )
        manager.sessions["test"] = runtime
        mock_db = MagicMock()
        result = await manager.stop(mock_db, "test")
        assert result.running is False
        assert result.status == "stopped"
        assert runtime.task is None or isinstance(runtime.task, asyncio.Task)
