from fastapi import APIRouter

router = APIRouter(prefix="/ops/system", tags=["System"])

@router.post("/force_checkpoint")
def force_checkpoint():
    try:
        from ops.cognitive.auto_checkpoint import write_revision_checkpoint
        write_revision_checkpoint()
        return {"status": "ok", "detail": "checkpoint written"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
