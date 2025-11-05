from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from google.cloud import firestore

router = APIRouter(prefix="/ctx")

def _fs():
    return firestore.Client()

class AddNoteBody(BaseModel):
    # aceptamos ambos nombres para compatibilidad
    text: Optional[str] = Field(default=None)
    note: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = None

    def merged_text(self) -> str:
        if self.text and isinstance(self.text, str):
            return self.text
        if self.note and isinstance(self.note, str):
            return self.note
        raise ValueError("field 'text' (o 'note') requerido")

@router.get("/ping")
def ping():
    return {"ok": True, "pong": True, "ns": "ctx"}

@router.get("/{owner}")
def get_ctx(owner: str):
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
        "text": body.merged_text(),
        "tags": body.tags or [],
        "ts": firestore.SERVER_TIMESTAMP,
    }
    ref.set({"notes": firestore.ArrayUnion([note_doc])}, merge=True)
    return {"ok": True, "appended": True, "ns": "ctx"}
