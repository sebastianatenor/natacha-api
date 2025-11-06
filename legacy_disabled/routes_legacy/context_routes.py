from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from google.cloud import firestore

router = APIRouter(prefix="/context")

def _fs():
    return firestore.Client()

class AddNoteBody(BaseModel):
    text: str
    tags: Optional[List[str]] = None

@router.get("/ping")
def ping():
    return {"ok": True, "pong": True}

@router.get("/{owner}")
def get_context(owner: str):
    ref = _fs().collection("context").document(owner)
    doc = ref.get()
    if not doc.exists:
        return {"owner": owner, "notes": []}
    data = doc.to_dict() or {}
    return {"owner": owner, "notes": data.get("notes", [])}

@router.post("/add_note/{owner}")
def add_note(owner: str, body: AddNoteBody):
    ref = _fs().collection("context").document(owner)
    note_doc = {
        "text": body.text,
        "tags": body.tags or [],
        "ts": firestore.SERVER_TIMESTAMP,
    }
    # Operación atómica: agrega la nota y crea el doc si no existe
    ref.set({"notes": firestore.ArrayUnion([note_doc])}, merge=True)
    return {"ok": True, "appended": True}
