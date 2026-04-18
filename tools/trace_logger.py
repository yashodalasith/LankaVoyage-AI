from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = WORKSPACE_ROOT / "logs"
OPTIMIZER_TRACE_FILE = LOGS_DIR / "optimizer_trace.jsonl"


def append_trace(event: str, payload: Dict[str, Any]) -> None:
    """Append a structured trace event to the optimizer trace log."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "payload": payload,
    }
    with OPTIMIZER_TRACE_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
