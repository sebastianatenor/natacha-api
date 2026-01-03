from fastapi import APIRouter
from ops.cognitive.pending_action import clear_pending

router = APIRouter(prefix="/ops/actions", tags=["actions"])


@router.post("/cancel")
def cancel_action():
    clear_pending()
    return {
        "status": "cancelled",
    }
