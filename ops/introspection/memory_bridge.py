"""
ops.introspection.memory_bridge
---------------------------------
Guarda resultados de introspección en la memoria persistente local.
"""

import json
from datetime import datetime
from pathlib import Path


def save_introspection_result(result: dict):
    """Guarda el resultado de introspección en memory_store.jsonl."""
    memory_path = Path("memory_store.jsonl")
    entry = {
        "timestamp": datetime.now().isoformat(),
        "kind": "introspection_result",
        "detail": result,
    }

    try:
        with memory_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"[OK] Result saved to {memory_path}")
    except Exception as e:
        print(f"[ERROR] Could not save introspection result: {e}")
