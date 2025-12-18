import json
from pathlib import Path
from datetime import datetime

MEMORY_PATH = Path("memory_store.jsonl")

def load_last_checkpoint():
    last = None
    if not MEMORY_PATH.exists():
        return None
    with MEMORY_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                if obj.get("kind") == "self_checkpoint":
                    last = obj
            except Exception:
                continue
    return last

def summary_already_exists(revision):
    with MEMORY_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                if obj.get("kind") == "executive_summary" and obj.get("revision") == revision:
                    return True
            except Exception:
                continue
    return False

def main():
    checkpoint = load_last_checkpoint()
    if not checkpoint:
        print("<0001f9e0> No hay checkpoint previo")
        return

    revision = checkpoint.get("revision")
    if summary_already_exists(revision):
        print("<0001f9e0> RESUMEN OMITIDO (ya existe)")
        print("Revisión:", revision)
        return

    observed = checkpoint.get("observed_state", {})
    semantic_loaded = observed.get("semantic", {}).get("loaded")

    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "kind": "executive_summary",
        "revision": revision,
        "confidence": "high",
        "summary": {
            "infra": "stable",
            "memory": "loaded",
            "context": "loaded",
            "semantic": "active" if semantic_loaded else "initializing",
            "global_state": "stable_with_pending_semantic"
        },
        "notes": (
            "Infraestructura y memoria estables. "
            "Cognición semántica en proceso de inicialización."
            if not semantic_loaded else
            "Sistema completamente operativo con cognición semántica activa."
        )
    }

    with MEMORY_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(summary, ensure_ascii=False) + "\n")

    print("<0001f9e0> RESUMEN EJECUTIVO GUARDADO")
    print("Revisión:", revision)
    print("Semantic loaded:", semantic_loaded)

if __name__ == "__main__":
    main()
