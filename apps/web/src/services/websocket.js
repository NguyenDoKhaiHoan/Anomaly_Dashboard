const WS_BASE = (import.meta.env.VITE_WS_BASE || "ws://localhost:8000").replace(/\/$/, "");

export function createStreamSocket(sessionId, onMessage) {
  const socket = new WebSocket(`${WS_BASE}/api/v1/streams/ws/${sessionId}`);
  socket.onmessage = (event) => {
    try { onMessage(JSON.parse(event.data)); } catch {}
  };
  return socket;
}
