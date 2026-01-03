from fastapi import APIRouter
from pathlib import Path
import json
import os

router = APIRouter(prefix="/ops/actions", tags=["actions"])

TIMELINE_PATH = Path(
    "/tmp/action_timeline.jsonl"
    if os.getenv("K_SERVICE")
    else "action_timeline.jsonl"
)


@router.get("/recent")
def recent_actions(limit: int = 10):
    if not TIMELINE_PATH.exists():
        return []

    lines = TIMELINE_PATH.read_text().splitlines()[-limit:]
    return [json.loads(l) for l in lines]
