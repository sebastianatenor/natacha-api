from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

from ops.timeline.writer import write_event
from ops.snapshots.writer import write_snapshot
from ops.system.checkpoint import create_checkpoint

router = APIRouter()


class ShadowAutoInput(BaseModel):
    text: str


@router.post("/system/shadow/auto_cycle")
def shadow_auto_cycle(payload: ShadowAutoInput):
    """
    Executes a full shadow cognitive cycle:
    - registers decision
    - writes snapshot
    - writes checkpoint
    """

    decision = {
        "decision": "accepted",
        "confidence": 0.85,
        "input": payload.text,
    }

    # 1️⃣ write shadow decision
    write_event(
        kind="shadow_decision",
        subsystem="cognitive",
        state="accepted",
        revision="v17",
        confidence=decision["confidence"],
        details=decision,
    )

    # 2️⃣ snapshot
    snapshot = write_snapshot(label="shadow-auto-cycle")

    # 3️⃣ checkpoint
    checkpoint = create_checkpoint("shadow-auto-cycle")

    return {
        "status": "ok",
        "mode": "shadow",
        "decision": decision,
        "snapshot": snapshot,
        "checkpoint": checkpoint,
        "timestamp": datetime.utcnow().isoformat(),
    }
