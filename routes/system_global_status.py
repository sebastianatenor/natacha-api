from fastapi import APIRouter

from routes.system_sync import system_sync_all
from routes.system_snapshot_engine import snapshot_engine_status
from routes.system_checkpoint_engine import checkpoint_engine_status
from routes.system_semantic import semantic_status
from routes.system_vector_engine import vector_status

router = APIRouter()

@router.get("/system/status/global")
def global_status():
    return {
        "semantic": semantic_status(),
        "vector": vector_status(),
        "snapshots": snapshot_engine_status(),
        "checkpoints": checkpoint_engine_status(),
        "sync": system_sync_all(),
        "mode": "pre-ml-unified",
    }
