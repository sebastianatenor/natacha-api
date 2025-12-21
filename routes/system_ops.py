from fastapi import APIRouter

router = APIRouter(prefix="/ops/system", tags=["system-ops"])

@router.post("/force-checkpoint")
def force_checkpoint():
    from ops.cognitive.auto_checkpoint import write_revision_checkpoint
    write_revision_checkpoint()
    return {"status": "ok", "action": "checkpoint_written"}

@router.post("/daily-snapshot")
def force_daily_snapshot():
    from ops.snapshots.daily_snapshot import write_daily_snapshot
    write_daily_snapshot()
    return {"status": "ok", "action": "daily_snapshot_written"}
