from fastapi import APIRouter
from pydantic import BaseModel
from ops.memory.note import write_memory_note

router = APIRouter(tags=["memory"])


class MemoryNoteIn(BaseModel):
    content: str
    tags: list[str] = []


@router.post("/memory/note")
def create_memory_note(payload: MemoryNoteIn):
    event = write_memory_note(
        content=payload.content,
        tags=payload.tags,
    )
    return {
        "status": "ok",
        "event": event,
    }
