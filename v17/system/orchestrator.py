# v17/system/orchestrator.py

"""
v17 Orchestrator
----------------
Arquitectura pura, determinística y sin efectos colaterales.

- No escribe memoria
- No crea proposals
- No ejecuta acciones
- Solo decide
"""

from v17.semantic.analyzer import semantic_analyze
from v17.gate.evaluator import evaluate_gate
from v17.contracts import SystemDecision


def orchestrate(text: str) -> SystemDecision:
    """
    Orquesta una decisión completa de forma pura.
    """

    semantic = semantic_analyze(text)
    gate = evaluate_gate(semantic)

    required_action = "human_decision" if gate.blocked else None

    return SystemDecision(
        semantic=semantic,
        gate=gate,
        required_action=required_action,
    )
