# v17/system/orchestrator.py

from v17.semantic.analyzer import semantic_analyze
from v17.gate.evaluator import evaluate_gate
from v17.contracts import SystemDecision


def orchestrate(text: str) -> SystemDecision:
    semantic = semantic_analyze(text)
    gate = evaluate_gate(semantic)

    required_action = "human_decision" if gate.blocked else None

    return SystemDecision(
        semantic=semantic,
        gate=gate,
        required_action=required_action,
    )
