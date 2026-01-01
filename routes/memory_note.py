# routes/memory_note.py

from fastapi import APIRouter
from pydantic import BaseModel
import json
from unified_core.memory_writer_v2 import memory_writer_v2

router = APIRouter(tags=["memory"])

class MemoryNoteIn(BaseModel):
    content: str
    tags: list[str] = []

@router.post("/memory/note")
def create_memory_note(payload: MemoryNoteIn):
    """
    Writes a memory note using MemoryWriterV2.
    content -> text
    structured fields -> meta
    """

    try:
        data = json.loads(payload.content)
    except Exception:
        data = {
            "kind": "memory_note",
            "raw": payload.content
        }

    record = memory_writer_v2.write(
        text=payload.content,
        meta=data,
        tags=payload.tags,
    )

    return {
        "status": "ok",
        "record": record,
    }
