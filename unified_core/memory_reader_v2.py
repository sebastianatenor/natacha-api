import json
from typing import List, Dict, Any
from unified_core.vectorstore.store import vector_store

MEMORY_PATH = "memory_store.jsonl"

class MemoryReaderV2:

    def load_recent(self, limit=20) -> List[Dict[str, Any]]:
        items = []
        try:
            with open(MEMORY_PATH, "r") as f:
                for line in f:
                    try:
                        items.append(json.loads(line))
                    except:
                        continue
        except:
            return []

        items = sorted(items, key=lambda x: x.get("timestamp", ""))
        return items[-limit:]

    def search_semantic(self, query: str, top_k=5):
        return vector_store.search(query, top_k=top_k)

    def search_tags(self, tag: str):
        items = []
        with open(MEMORY_PATH, "r") as f:
            for line in f:
                obj = json.loads(line)
                if tag in (obj.get("tags") or []):
                    items.append(obj)
        return items


memory_reader_v2 = MemoryReaderV2()
