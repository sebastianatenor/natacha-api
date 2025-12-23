"""
ops.cognitive.symbolic_rules
----------------------------
Motor simbólico PASIVO (Mode F).
Lee memoria.
Infiera estados.
NO ejecuta acciones.
NO toca infraestructura.
"""

import json
from pathlib import Path
from datetime import datetime

MEMORY_PATH = Path("memory_store.jsonl")

# --------------------------------------------------
# Helpers
# --------------------------------------------------

def load_last(kind: str):
    last = None
    if not MEMORY_PATH.exists():
        return None
    with MEMORY_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                if obj.get("kind") == kind:
                    last = obj
            except Exception:
                continue
    return last


# --------------------------------------------------
# Regla F-1: Semantic pending
# --------------------------------------------------
# IF semantic.loaded == False
# THEN state = semantic_pending
# --------------------------------------------------

def rule_semantic_pending():
    checkpoint = load_last("self_checkpoint")
    if not checkpoint:
        return None

    semantic_loaded = (
        checkpoint
        .get("observed_state", {})
        .get("semantic", {})
        .get("loaded")
    )

    if semantic_loaded is False:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "kind": "symbolic_inference",
            "rule": "semantic_pending",
            "revision": checkpoint.get("revision"),
            "confidence": "high",
            "decision": {
                "state": "semantic_pending",
                "severity": "low",
                "action": "monitor"
            },
            "notes": (
                "Cognición semántica aún no activa. "
                "Sistema estable. Monitoreo pasivo."
            )
        }

    return None


# --------------------------------------------------
# Runner
# --------------------------------------------------

def run_symbolic_rules():
    results = []
    r1 = rule_semantic_pending()
    if r1:
        results.append(r1)
    return results


if __name__ == "__main__":
    inferences = run_symbolic_rules()
    if not inferences:
        print("<0001f9e0> SIN INFERENCIAS (estado estable)")
    else:
        for inf in inferences:
            print("<0001f9e0> INFERENCIA SIMBÓLICA")
            print("Regla:", inf["rule"])
            print("Estado:", inf["decision"]["state"])
            print("Severidad:", inf["decision"]["severity"])
