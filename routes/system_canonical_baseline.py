from fastapi import APIRouter
from unified_core.canonical_writer import write_canonical_event
import uuid

router = APIRouter(tags=["system"])

@router.post("/system/baseline/lock")
def lock_baseline():
    meta = {
        "id": uuid.uuid4().hex,
        "kind": "executive_decision",
        "label": "PRE-ML baseline locked",
        "scope": "global",
        "canonical": True,
    }

    record = write_canonical_event(
        meta=meta,
        tags=["executive", "canonical", "baseline"]
    )

    return {"status": "ok", "record": record}
