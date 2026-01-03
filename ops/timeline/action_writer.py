"""
Action Timeline Writer — AGENTE_VERAZ
Append-only JSONL
"""

from datetime import datetime
from typing import Dict
import json
from pathlib import Path
import os

TIMELINE_PATH = Path(
    "/tmp/action_timeline.jsonl"
    if os.getenv("K_SERVICE")
    else "action_timeline.jsonl"
)


def write_action_event(kind: str, signal: Dict, result: Dict):
    event = {
        "kind": kind,
        "signal": signal,
        "result": result,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    TIMELINE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(TIMELINE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    print("[ACTION_EVENT]", event)
    return event
