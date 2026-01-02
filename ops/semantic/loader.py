# ops/semantic/loader.py
"""
Semantic Loader — AGENTE_VERAZ (STUB)

Este módulo:
- NO carga modelos automáticamente
- NO asume disponibilidad de engines
- SOLO registra hechos verificables

Si no hay engine → se registra "unloaded"
"""

from ops.cognitive.semantic_registry import register_semantic_event


def init_semantic_engine(*, force: bool = False) -> dict:
    """
    Inicialización explícita (stub).

    Si algún día vuelve HF u otro engine,
    este archivo será el único lugar a modificar.
    """

    register_semantic_event(
        state="unloaded",
        confidence="high",
        source="semantic_loader_stub",
    )

    return {
        "status": "noop",
        "reason": "semantic_engine_not_configured",
    }
