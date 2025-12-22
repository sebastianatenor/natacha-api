from fastapi import APIRouter
from ops.memory.semantic_indexer import index_memory_notes

router = APIRouter(tags=["memory"])

@router.post("/memory/index/notes")
def index_notes():
    count = index_memory_notes()
    return {
        "status": "ok",
        "indexed": count
    }
