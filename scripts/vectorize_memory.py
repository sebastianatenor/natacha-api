import os
from unified_core.memory_lazy import get_memory_index
from unified_core.vectorstore.store import vector_store
from unified_core.semantic_core import get_semantic_core

def vectorize_memory(limit: int = 500):
    print("[VECTORIZE] Starting memory vectorization")

    semantic = get_semantic_core()
    semantic.ensure_loaded()

    memory = get_memory_index()

    if not memory.store_loaded:
        raise RuntimeError("Memory store not loaded")

    items = memory.list_recent(limit=limit)

    print(f"[VECTORIZE] Items to vectorize: {len(items)}")

    count = 0
    for item in items:
        text = item.get("text")
        if not text:
            continue

        meta = {
            "tags": item.get("tags", []),
            "source": "memory_ndjson",
        }

        vector_store.add(text=text, meta=meta)
        count += 1

    print(f"[VECTORIZE] Done. Vectorized {count} items")

if __name__ == "__main__":
    vectorize_memory()
