import os
from unified_core.memory_lazy import get_memory_index
from unified_core.vectorstore.store import vector_store

def vectorize_memory(limit: int = 500):
    memory = get_memory_index()
    items = memory.list_recent(limit=limit)

    print(f"[VECTORIZE] Vectorizing {len(items)} items")

    count = 0
    for item in items:
        text = item.get("text")
        if not text:
            continue

        meta = {
            "tags": item.get("tags", []),
            "timestamp": item.get("meta", {}).get("timestamp"),
            "source": "ndjson_memory",
        }

        vector_store.add(text=text, meta=meta)
        count += 1

    print(f"[VECTORIZE] Done. Stored {count} vectors.")

if __name__ == "__main__":
    vectorize_memory()
