# ops/system/restore_from_memory.py

import json
from unified_core.memory_paths import get_canonical_memory_path


def restore_cognitive_state():
    path = get_canonical_memory_path()

    print("[RESTORE] path:", path)
    print("[RESTORE] exists:", path.exists())

    if not path.exists():
        return {
            "restored": False,
            "reason": "memory_file_not_found"
        }

    checkpoints = []
    executive_decisions = []

    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i < 5:
                print("[RESTORE] sample line:", line[:200])
            try:
                rec = json.loads(line)
            except Exception as e:
                print("[RESTORE] json error:", e)
                continue

            meta = rec.get("meta", {})
            if meta.get("kind") == "executive_decision" and meta.get("canonical") is True:
                executive_decisions.append(meta)

            if meta.get("kind") in ("checkpoint", "cognitive_state"):
                checkpoints.append(rec)

    if not checkpoints and not executive_decisions:
        return {
            "restored": False,
            "reason": "no_restore_state_loaded"
        }

    # PRE-ML RULE:
    # Executive decisions alone define baseline if no checkpoints exist
    return {
        "restored": True,
        "mode": "pre-ml-unified",
        "baseline": (
            checkpoints[-1].get("label")
            if checkpoints else
            "executive-baseline"
        ),
        "executive_decisions": len(executive_decisions),
    }
