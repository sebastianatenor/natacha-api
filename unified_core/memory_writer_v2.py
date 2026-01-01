import json
import uuid
from datetime import datetime
from typing import Dict, Any
from unified_core.vectorstore.store import vector_store
from unified_core.memory_paths import get_canonical_memory_path

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

        path = get_canonical_memory_path()

        # Persistencia NDJSON (CANÓNICA)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        # Persistencia vectorial (si está activa)
        try:
            vector_store.add(text, meta)
        except Exception:
            pass

        return record

memory_writer_v2 = MemoryWriterV2()
