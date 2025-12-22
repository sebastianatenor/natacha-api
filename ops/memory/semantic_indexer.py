from unified_core.semantic_store import upsert_embedding
from unified_core.memory_paths import get_canonical_memory_path
import json

def index_memory_notes():
    """
    Indexa memory_note.content en el store semántico
    """
    path = get_canonical_memory_path()
    if not path.exists():
        return 0

    indexed = 0

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                event = json.loads(line)
            except Exception:
                continue

            if event.get("kind") != "memory_note":
                continue

            content = event.get("content")
            if not content:
                continue

            upsert_embedding(
                text=content,
                metadata={
                    "kind": "memory_note",
                    "timestamp": event.get("timestamp"),
                    "tags": event.get("tags", []),
                }
            )
            indexed += 1

    return indexed
