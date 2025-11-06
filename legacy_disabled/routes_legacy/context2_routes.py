from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from google.cloud import firestore

router = APIRouter(prefix="/context2")

def _fs():
    return firestore.Client()

class AddNoteBody(BaseModel):
    text: str
    tags: Optional[List[str]] = None

@router.get("/ping")
def ping():
    return {"ok": True, "pong": True, "ns": "context2"}

@router.post("/add_note/{owner}")
def add_note(owner: str, body: AddNoteBody):
    # Igual que /context/add_note, para compatibilidad
    ref = _fs().collection("context").document(owner)
    note_doc = {
        "text": body.text,
        "tags": body.tags or [],
        "ts": firestore.SERVER_TIMESTAMP,
    }
    ref.set({"notes": firestore.ArrayUnion([note_doc])}, merge=True)
    return {"ok": True, "appended": True, "ns": "context2"}
