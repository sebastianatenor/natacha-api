"""
Semantic Decider — AGENTE_VERAZ

Fuente única de decisión semántica.
- Heurística: SIEMPRE
- Embeddings: solo si están cargados
NO ejecuta acciones
"""

from typing import Dict, Any

from ops.cognitive.semantic_gate import semantic_allowed
from ops.semantic.engine import get_engine


def decide_semantic_signal(text: str) -> Dict[str, Any]:
    caps = semantic_allowed()

    engine = get_engine()
    if not engine:
        return {
            "method": "none",
            "signal": None,
            "caps": caps,
            "reason": "engine_not_available",
        }

    analysis = engine.analyze(text)
    signal = analysis.signals.dict()

    # Embeddings todavía NO cambian decisiones
    method = "heuristic"
    if caps.get("embeddings"):
        method = "heuristic+embeddings"

    return {
        "method": method,
        "signal": signal,
        "caps": caps,
    }
