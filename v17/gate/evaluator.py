# v17/gate/evaluator.py

from v17.contracts import SemanticFrame, GateDecision


def evaluate_gate(semantic: SemanticFrame) -> GateDecision:
    if semantic.intent == "implicit_action" and semantic.risk_level == "high" and semantic.confidence >= 0.8:
        return GateDecision(
            blocked=True,
            reason="implicit_high_risk_action",
        )

    return GateDecision(
        blocked=False,
        reason="allowed",
    )
