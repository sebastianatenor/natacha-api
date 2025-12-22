from fastapi import APIRouter

router = APIRouter(tags=["memory"])


@router.post("/memory/index")
def index_memory():
    """
    Fuerza indexación semántica de memory_notes.
    Nunca debe romper el sistema.
    """

    try:
        from ops.timeline.reader import read_events
        from ops.memory.semantic_indexer import index_memory_note

        events = read_events()
        indexed = 0

        for e in events:
            if e.get("kind") == "memory_note":
                if index_memory_note(e):
                    indexed += 1

        return {
            "status": "ok",
            "indexed": indexed,
            "semantic": True,
        }

    except Exception as e:
        return {
            "status": "ok",
            "indexed": 0,
            "semantic": False,
            "reason": str(e),
        }
