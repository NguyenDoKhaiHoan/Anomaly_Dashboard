from __future__ import annotations
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token, get_current_user
from app.db_models.stream_session import StreamSession
from app.schemas.stream import StreamControlResponse, StreamSessionCreate, StreamSessionRead
from app.services.stream.session_manager import session_manager
from app.services.stream.sse_manager import format_sse
from app.services.stream.websocket_manager import websocket_manager
from app.utils.ids import generate_session_id

router = APIRouter(prefix="/streams", tags=["streams"])

@router.get("/sessions", response_model=list[StreamSessionRead])
def list_sessions(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(StreamSession).filter(StreamSession.user_id == current_user.id).order_by(StreamSession.created_at.desc()).all()

@router.post("/sessions", response_model=StreamSessionRead)
def create_session(payload: StreamSessionCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    session_obj = StreamSession(
        id=generate_session_id(), user_id=current_user.id, stream_type=payload.stream_type,
        model_key=payload.model_key, dataset_key=payload.dataset_key, asset_symbol=payload.asset_symbol,
        status="created", stream_interval=payload.stream_interval, threshold_override=payload.threshold_override,
    )
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)
    session_manager.register_from_db(session_obj)
    return session_obj

@router.post("/sessions/{session_id}/start", response_model=StreamControlResponse)
async def start_session(session_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    session_obj = db.query(StreamSession).filter(StreamSession.id == session_id, StreamSession.user_id == current_user.id).first()
    if session_obj is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy session.")
    runtime = await session_manager.start(db, session_obj)
    return StreamControlResponse(session_id=runtime.session_id, status=runtime.status, active_sessions=session_manager.active_count(), queue_size=runtime.queue.qsize())

@router.post("/sessions/{session_id}/stop", response_model=StreamControlResponse)
async def stop_session(session_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    session_obj = db.query(StreamSession).filter(StreamSession.id == session_id, StreamSession.user_id == current_user.id).first()
    if session_obj is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy session.")
    runtime = await session_manager.stop(db, session_id)
    return StreamControlResponse(session_id=runtime.session_id, status=runtime.status, active_sessions=session_manager.active_count(), queue_size=runtime.queue.qsize())

@router.patch("/sessions/{session_id}", response_model=StreamControlResponse)
async def update_session(session_id: str, payload: StreamSessionCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    session_obj = db.query(StreamSession).filter(StreamSession.id == session_id, StreamSession.user_id == current_user.id).first()
    if session_obj is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy session.")
    
    # Update session params in DB
    session_obj.stream_interval = payload.stream_interval
    session_obj.threshold_override = payload.threshold_override
    db.commit()
    
    # Update runtime if running
    runtime = session_manager.sessions.get(session_id)
    if runtime:
        session_manager.update_runtime(runtime, payload.stream_interval, payload.threshold_override)
    
    return StreamControlResponse(
        session_id=session_id,
        status=runtime.status if runtime else session_obj.status,
        active_sessions=session_manager.active_count(),
        queue_size=runtime.queue.qsize() if runtime else 0
    )

@router.get("/sessions/{session_id}/runtime")
def runtime_state(session_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    runtime = session_manager.sessions.get(session_id)
    if runtime is not None and runtime.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Không tìm thấy runtime session.")
    
    if runtime is None:
        session_obj = db.query(StreamSession).filter(StreamSession.id == session_id, StreamSession.user_id == current_user.id).first()
        if session_obj is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy session.")
        runtime = session_manager.register_from_db(session_obj)
    
    return runtime.counters | {"running": runtime.running, "status": runtime.status}

@router.get("/sessions/{session_id}/events")
async def sse_events(session_id: str, token: str = Query(...)):
    runtime = session_manager.sessions.get(session_id)
    if runtime is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy runtime session.")
    try:
        user_id = int(decode_token(token))
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Token không hợp lệ.") from exc
    if runtime.user_id != user_id:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập session này.")
    async def event_generator():
        while True:
            payload = await runtime.queue.get()
            yield format_sse(payload)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.websocket("/ws/{session_id}")
async def websocket_events(websocket: WebSocket, session_id: str):
    runtime = session_manager.sessions.get(session_id)
    if runtime is None:
        await websocket.close(code=4404)
        return
    await websocket_manager.connect(session_id, websocket)
    try:
        while True:
            await asyncio.sleep(30)
            await websocket.send_json({"type": "heartbeat", "session_id": session_id})
    except WebSocketDisconnect:
        websocket_manager.disconnect(session_id, websocket)
