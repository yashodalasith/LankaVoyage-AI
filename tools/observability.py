from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = WORKSPACE_ROOT / "logs"
RUN_LOG_FILE = LOGS_DIR / "run.log"
EVENT_LOG_FILE = LOGS_DIR / "events.jsonl"


def log_event(stage: str, event: str, payload: Dict[str, Any], echo: bool = True) -> None:
    """Write one structured observability event to logs and optionally print it live."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    record = {
        "timestamp": timestamp,
        "stage": stage,
        "event": event,
        "payload": payload,
    }

    with EVENT_LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    line = f"[{timestamp}] [{stage}] {event} | {json.dumps(payload, ensure_ascii=False)}"
    with RUN_LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")

    if echo:
        print(line, flush=True)
