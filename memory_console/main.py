import os
from typing import Optional, Any, Dict
from fastapi import FastAPI, HTTPException, Header, Body
from google.cloud import firestore

app = FastAPI()

def _check_auth(authorization: Optional[str]):
    expected = os.getenv("MEM_CONSOLE_TOKEN", "")
    if not expected:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1]
    if token != expected:
        raise HTTPException(status_code=403, detail="Invalid token")

def _db():
    # Prefer explicit project to avoid metadata edge cases
    try:
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        return firestore.Client(project=project) if project else firestore.Client()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"firestore init error: {e}")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"service": "natacha-memory-console"}

@app.post("/mem/set")
def mem_set(
    payload: Dict[str, Any] = Body(...),
    collection: str = "natacha_memory",
    doc_id: Optional[str] = None,
    authorization: Optional[str] = Header(default=None),
):
    _check_auth(authorization)
    try:
        db = _db()
        if not doc_id:
            ref = db.collection(collection).document()
            ref.set(payload)
            return {"ok": True, "collection": collection, "doc_id": ref.id}
        else:
            ref = db.collection(collection).document(doc_id)
            ref.set(payload, merge=True)
            return {"ok": True, "collection": collection, "doc_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"mem_set error: {e}")

@app.get("/mem/get")
def mem_get(
    collection: str,
    doc_id: str,
    authorization: Optional[str] = Header(default=None),
):
    _check_auth(authorization)
    try:
        db = _db()
        snap = db.collection(collection).document(doc_id).get()
        if not snap.exists:
            raise HTTPException(status_code=404, detail="not found")
        return {"ok": True, "collection": collection, "doc_id": doc_id, "data": snap.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"mem_get error: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
