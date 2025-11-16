from fastapi import APIRouter
from gcs_sync import upload_state, download_state, ensure_state_file

router = APIRouter(prefix="/ops", tags=["affective-sync"])

@router.get("/affective-sync")
def get_sync_status():
    ensure_state_file()
    return {"status": "ok", "message": "Memoria afectiva sincronizada localmente"}

@router.post("/affective-sync")
def trigger_sync():
    ensure_state_file()
    download_state()
    upload_info = upload_state()
    return {"status": "ok", "sync": upload_info}
