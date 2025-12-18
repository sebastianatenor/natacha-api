import json
import requests
from datetime import datetime
from pathlib import Path

API = "https://natacha-api-422255208682.us-central1.run.app/ops/system/full_status"
MEMORY_PATH = Path("memory_store.jsonl")

def load_last_checkpoint():
    if not MEMORY_PATH.exists():
        return None
    last = None
    with MEMORY_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                if obj.get("kind") == "self_checkpoint":
                    last = obj
            except Exception:
                continue
    return last

def main():
    state = requests.get(API).json()
    revision = state.get("runtime", {}).get("revision")

    last = load_last_checkpoint()
    if last and last.get("revision") == revision:
        print("<0001f9e0> AUTO-CHECKPOINT OMITIDO (misma revisión)")
        print("Revisión:", revision)
        return

    checkpoint = {
        "timestamp": datetime.utcnow().isoformat(),
        "kind": "self_checkpoint",
        "revision": revision,
        "user_id": "system",
        "observed_state": state,
        "self_reported_state": {
            "infra": "stable",
            "memory": "loaded",
            "context": "loaded",
            "semantic": state.get("semantic", {}),
            "notes": "Checkpoint automático por cambio de revisión."
        },
        "confidence": "high",
        "mode": "B"
    }

    with MEMORY_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(checkpoint, ensure_ascii=False) + "\n")

    print("<0001f9e0> AUTO-CHECKPOINT GUARDADO")
    print("Revisión:", revision)
    print("Timestamp:", checkpoint["timestamp"])

if __name__ == "__main__":
    main()
