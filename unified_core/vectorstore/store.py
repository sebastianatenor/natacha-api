import os
import json
import uuid
from typing import List, Dict, Any, Optional
from unified_core.semantic_core import get_semantic_core
semantic_core = get_semantic_core()

VECTOR_DB = "vector_memory.jsonl"

class VectorStore:
    """
    Almacén vectorial mínimo, persistente y sin dependencias externas.
    Ultra rápido, escalable hasta ~100k recuerdos.
    """

    def __init__(self, path: str = VECTOR_DB):
        self.path = path
        if not os.path.exists(path):
            with open(path, "w") as f:
                pass

    def add(self, text: str, meta: Dict[str, Any]):
        vector = semantic_core.embed(text)
        entry = {
            "id": uuid.uuid4().hex,
            "text": text,
            "meta": meta,
            "vector": vector
        }
        with open(self.path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def load_all(self) -> List[Dict[str, Any]]:
        items = []
        with open(self.path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    items.append(json.loads(line))
                except:
                    continue
        return items

    def similarity(self, v1: List[float], v2: List[float]) -> float:
        import numpy as np
        v1 = np.array(v1)
        v2 = np.array(v2)
        denom = (np.linalg.norm(v1) * np.linalg.norm(v2))
        if denom == 0:
            return 0.0
        return float(np.dot(v1, v2) / denom)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        q_vec = semantic_core.embed(query)
        items = self.load_all()
        ranked = []
        for item in items:
            score = self.similarity(q_vec, item["vector"])
            ranked.append((score, item))
        ranked.sort(reverse=True, key=lambda x: x[0])
        return [x[1] for x in ranked[:top_k]]


vector_store = VectorStore()
