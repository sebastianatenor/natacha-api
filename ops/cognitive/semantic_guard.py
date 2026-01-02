# ops/cognitive/semantic_guard.py
"""
Semantic Startup Guard — AGENTE_VERAZ

Garantiza que el sistema arranca con un estado semántico
explícito y verificable.

NO carga engines.
NO infiere.
NO depende de HF.
"""

from ops.cognitive.semantic_registry import read_semantic_state, register_semantic_event


def semantic_startup_guard() -> dict:
    """
    Asegura estado semántico inicial.
    Se ejecuta UNA vez en startup.
    """

    current = read_semantic_state()

    if current is not None:
        # Ya existe un estado explícito → no tocar
        return {
            "status": "noop",
            "reason": "semantic_state_already_set",
            "state": current.get("state"),
        }

    # Estado explícito por defecto
    register_semantic_event(
        state="unloaded",
        confidence="high",
        source="semantic_startup_guard",
    )

    return {
        "status": "initialized",
        "state": "unloaded",
    }
