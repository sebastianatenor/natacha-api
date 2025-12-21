from fastapi import APIRouter

router = APIRouter(prefix="/ops/system", tags=["system"])

@router.post("/daily-snapshot")
def daily_snapshot():
    from ops.snapshots.daily_snapshot import write_daily_snapshot
    write_daily_snapshot()
    return {"status": "ok", "action": "daily_snapshot_written"}
