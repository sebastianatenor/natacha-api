from fastapi import APIRouter

router = APIRouter()


@router.get("/system/status/global")
def global_status():
    return {
        "semantic": _semantic(),
        "vector": _vector(),
        "snapshots": _snapshots(),
        "checkpoints": _checkpoints(),
        "sync": _sync(),
        "mode": "pre-ml-unified",
    }


def _semantic():
    try:
        from routes.system_semantic import semantic_status
        return semantic_status()
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _vector():
    try:
        from routes.system_vector_engine import vector_status
        return vector_status()
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _snapshots():
    try:
        from routes.system_snapshot_engine import snapshot_engine_status
        return snapshot_engine_status()
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _checkpoints():
    try:
        from routes.system_checkpoint_engine import checkpoint_engine_status
        return checkpoint_engine_status()
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _sync():
    try:
        from routes.system_sync import get_global_sync_status
        return get_global_sync_status()
    except Exception as e:
        return {"status": "error", "detail": str(e)}
