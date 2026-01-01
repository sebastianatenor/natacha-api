# ops/system/runtime_probe.py

from typing import Dict

def runtime_verification() -> Dict[str, bool]:
    """
    Única fuente de verdad runtime (PRE-ML).
    Devuelve qué puede afirmarse con certeza.
    """

    return {
        "health": True,                 # /health existe
        "system_state": True,           # /get_system_state existe
        "guardrail": True,              # /system/guardrail/check existe
        "diagnosis": False,             # NO existe
        "vector_engine": False,         # stub
        "semantic_embeddings": False,   # no embeddings
        "agent_autonomy": False,        # bloqueado
    }
