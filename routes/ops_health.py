from fastapi import APIRouter
from fastapi.responses import JSONResponse
import logging
from routes.db_util import get_db

router = APIRouter()

@router.get("/ops/ping")
def ops_ping():
    # No toca Firestore, puro sanity
    return {"ok": True, "service": "natacha-api", "component": "ops", "note": "health-router"}

@router.get("/ops/_debug_db")
def ops_debug_db():
    try:
        db = get_db()
        cols = [c.id for c in db.collections()]
        return {"ok": True, "collections": cols}
    except Exception as e:
        logging.exception("ops_debug_db failed")
        return JSONResponse({"ok": False, "err": f"{e.__class__.__name__}: {e}"}, status_code=503)
