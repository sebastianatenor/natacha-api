import json
import uuid
from datetime import datetime
from typing import Dict, Any

from unified_core.vectorstore.store import vector_store

MEMORY_PATH = "memory_store.jsonl"

class MemoryWriterV2:

    def write(self, text: str, meta: Dict[str, Any] = None, tags=None):
        meta = meta or {}
        record = {
            "id": uuid.uuid4().hex,
            "timestamp": datetime.utcnow().isoformat(),
            "text": text,
            "meta": meta,
            "tags": tags or []
        }

        # --- Persistencia en memoria histórica ---
        with open(MEMORY_PATH, "a") as f:
            f.write(json.dumps(record) + "\n")

        # --- Persistencia vectorial ---
        vector_store.add(text, meta)

        return record


memory_writer_v2 = MemoryWriterV2()
