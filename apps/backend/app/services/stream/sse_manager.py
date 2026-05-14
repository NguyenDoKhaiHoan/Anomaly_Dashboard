from __future__ import annotations
import json

def format_sse(data: dict, event: str | None = None) -> str:
    payload = json.dumps(data, ensure_ascii=False, default=str)
    if event:
        return f"event: {event}\ndata: {payload}\n\n"
    return f"data: {payload}\n\n"
