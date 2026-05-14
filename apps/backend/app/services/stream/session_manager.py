from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
from time import perf_counter
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.logging import logger
from app.db_models.anomaly_event import AnomalyEvent
from app.db_models.dataset_registry import DatasetRegistry
from app.db_models.stream_session import StreamSession
from app.services.alerts.dispatcher import dispatch_alerts
from app.services.drift.monitor import drift_monitor
from app.services.inference.registry import detector_registry
from app.services.preprocessing.fraud_features import engineer_fraud_features
from app.services.preprocessing.iot_features import engineer_iot_features
from app.services.stream.simulators.credit_stream import CreditCardStream
from app.services.stream.simulators.iot_stream import IoTSensorStream
from app.services.stream.websocket_manager import websocket_manager
from app.utils.time import utc_now

@dataclass
class RuntimeSession:
    session_id: str
    user_id: int
    stream_type: str
    model_key: str
    dataset_key: str | None = None
    asset_symbol: str | None = None
    stream_interval: float = 1.0
    threshold_override: float | None = None
    status: str = "created"
    running: bool = False
    queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue(maxsize=300))
    task: asyncio.Task | None = None
    counters: dict = field(default_factory=lambda: {"total_events": 0, "total_anomalies": 0, "latest_score": None})
    runtime_state: dict = field(default_factory=dict)

class SessionManager:
    def __init__(self):
        self.sessions: dict[str, RuntimeSession] = {}

    def active_count(self) -> int:
        return sum(1 for session in self.sessions.values() if session.running)

    def register_from_db(self, session_obj: StreamSession) -> RuntimeSession:
        runtime = RuntimeSession(
            session_id=session_obj.id,
            user_id=session_obj.user_id,
            stream_type=session_obj.stream_type,
            model_key=session_obj.model_key,
            dataset_key=session_obj.dataset_key,
            asset_symbol=session_obj.asset_symbol,
            stream_interval=session_obj.stream_interval,
            threshold_override=session_obj.threshold_override,
            status=session_obj.status,
        )
        self.sessions[session_obj.id] = runtime
        return runtime

    def update_runtime(self, runtime: RuntimeSession, stream_interval: float | None = None, threshold_override: float | None = None) -> None:
        if stream_interval is not None:
            runtime.stream_interval = stream_interval
        if threshold_override is not None:
            runtime.threshold_override = threshold_override

    def _resolve_dataset_path(self, db: Session, dataset_key: str | None) -> str | None:
        if not dataset_key:
            return None
        dataset = db.query(DatasetRegistry).filter(DatasetRegistry.key == dataset_key).first()
        return dataset.path if dataset else None

    def _build_streamer(self, runtime: RuntimeSession, db: Session):
        dataset_path = self._resolve_dataset_path(db, runtime.dataset_key)
        if runtime.stream_type == "credit_card":
            return CreditCardStream(dataset_path=dataset_path)
        if runtime.stream_type == "iot_sensor":
            return IoTSensorStream(dataset_path=dataset_path)
        raise ValueError(f"Unsupported stream_type: {runtime.stream_type}")

    def _preprocess(self, runtime: RuntimeSession, raw_event: dict, detector):
        if runtime.stream_type == "credit_card":
            return engineer_fraud_features(raw_event, runtime.runtime_state)
        if runtime.stream_type == "iot_sensor":
            return engineer_iot_features(raw_event, runtime.runtime_state, getattr(detector, "feature_names", None))
        return raw_event

    async def start(self, db: Session, session_obj: StreamSession) -> RuntimeSession:
        runtime = self.sessions.get(session_obj.id) or self.register_from_db(session_obj)
        if runtime.running:
            return runtime
        runtime.running = True
        runtime.status = "running"
        runtime.task = asyncio.create_task(self._run_loop(runtime))
        session_obj.status = "running"
        db.add(session_obj)
        db.commit()
        db.refresh(session_obj)
        return runtime

    async def stop(self, db: Session, session_id: str) -> RuntimeSession:
        runtime = self.sessions[session_id]
        runtime.running = False
        runtime.status = "stopped"
        if runtime.task:
            runtime.task.cancel()
            try:
                await runtime.task
            except asyncio.CancelledError:
                pass
            runtime.task = None
        session_obj = db.query(StreamSession).filter(StreamSession.id == session_id).first()
        if session_obj:
            session_obj.status = "stopped"
            db.add(session_obj)
            db.commit()
        return runtime

    async def _run_loop(self, runtime: RuntimeSession) -> None:
        db = SessionLocal()
        try:
            session_obj = db.query(StreamSession).filter(StreamSession.id == runtime.session_id).first()
            if session_obj is None:
                runtime.running = False
                return
            detector = detector_registry.get(runtime.model_key)
            streamer = self._build_streamer(runtime, db)
            while runtime.running:
                started = perf_counter()
                raw_event = streamer.next_event()
                features = self._preprocess(runtime, raw_event, detector)
                prediction = detector.predict(raw_event, features, runtime.runtime_state, runtime.threshold_override)
                latency_ms = (perf_counter() - started) * 1000.0
                runtime.counters["total_events"] += 1
                runtime.counters["latest_score"] = prediction.anomaly_score
                if prediction.is_anomaly:
                    runtime.counters["total_anomalies"] += 1
                drift_flag = drift_monitor.check(runtime.runtime_state.setdefault("drift_monitor", {}), prediction.anomaly_score)
                reasons = list(prediction.reasons)
                if drift_flag:
                    reasons.append("possible_concept_drift")
                event_payload = {
                    "session_id": runtime.session_id,
                    "stream_type": runtime.stream_type,
                    "model_key": runtime.model_key,
                    "timestamp": utc_now(),
                    "raw_event": raw_event,
                    "features": features,
                    "anomaly_score": float(prediction.anomaly_score),
                    "is_anomaly": bool(prediction.is_anomaly),
                    "reasons": reasons,
                    "detector_latency_ms": float(latency_ms),
                    "summary": {
                        "total_events": runtime.counters["total_events"],
                        "total_anomalies": runtime.counters["total_anomalies"],
                        "running": runtime.running,
                        "latest_score": runtime.counters["latest_score"],
                    },
                }
                event_db = AnomalyEvent(
                    session_id=runtime.session_id,
                    user_id=runtime.user_id,
                    stream_type=runtime.stream_type,
                    asset_symbol=runtime.asset_symbol,
                    model_key=runtime.model_key,
                    raw_payload=raw_event,
                    feature_payload=features,
                    anomaly_score=float(prediction.anomaly_score),
                    is_anomaly=bool(prediction.is_anomaly),
                    reasons=reasons,
                    detector_latency_ms=float(latency_ms),
                )
                db.add(event_db)
                db.commit()
                db.refresh(event_db)
                notifications = dispatch_alerts(db, runtime.user_id, event_db.id, event_payload, runtime.runtime_state.setdefault("alerts", {}))
                event_payload["notification_count"] = len(notifications)
                if runtime.queue.full():
                    try:
                        runtime.queue.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                await runtime.queue.put(event_payload)
                await websocket_manager.broadcast(runtime.session_id, event_payload)
                await asyncio.sleep(runtime.stream_interval)
        except asyncio.CancelledError:
            logger.info("Cancelled session loop: %s", runtime.session_id)
            raise
        except Exception as exc:
            logger.exception("Session loop crashed for %s: %s", runtime.session_id, exc)
            runtime.status = "error"
            runtime.running = False
        finally:
            db.close()

session_manager = SessionManager()
