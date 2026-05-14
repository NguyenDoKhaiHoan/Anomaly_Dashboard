from __future__ import annotations
from uuid import uuid4
def generate_session_id() -> str:
    return uuid4().hex
