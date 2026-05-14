from __future__ import annotations
from collections import defaultdict
from fastapi import WebSocket

class WebSocketSessionManager:
    def __init__(self):
        self.connections = defaultdict(list)

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[session_id].append(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        self.connections[session_id] = [item for item in self.connections.get(session_id, []) if item != websocket]

    async def broadcast(self, session_id: str, payload: dict) -> None:
        alive = []
        for websocket in self.connections.get(session_id, []):
            try:
                await websocket.send_json(payload)
                alive.append(websocket)
            except Exception:
                continue
        self.connections[session_id] = alive

websocket_manager = WebSocketSessionManager()
