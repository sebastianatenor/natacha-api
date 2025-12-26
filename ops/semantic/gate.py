# ops/semantic/gate.py

from typing import Optional, Dict, Any

from ops.cognitive.proposals.writer import write_proposal
from ops.cognitive.decisions.resolver import is_proposal_accepted
from ops.semantic.schema import SemanticAnalysis


def semantic_gate(
    analysis: SemanticAnalysis,
    source: str = "semantic.analyze",
) -> Optional[Dict[str, Any]]:
    """
    Semantic Gate (B16.4)

    - NO ejecuta acciones
    - Detecta acciones implícitas de alto riesgo
    - Bloquea por defecto
    - Permite continuar SOLO si existe una decisión ACCEPTED
    """

    signals = analysis.signals

    if (
        signals.intent == "implicit_action"
        and signals.risk_level == "high"
    ):
        proposal_data = {
            "title": "Implicit high-risk action detected",
            "description": (
                "The user input implies an automatic action without confirmation. "
                "Execution must be reviewed before proceeding."
            ),
            "rationale": (
                "Semantic engine detected an implicit action combined with "
                "automation markers, which is classified as high risk."
            ),
            "kind": "system",
            "status": "proposed",
            "confidence": signals.confidence,
            "source_revision": "B16.4",
            "source": source,
        }

        proposal = write_proposal(proposal_data)

        # 🔐 B16.4 — decision-based unlock
        if is_proposal_accepted(proposal.id):
            return {
                "gate": "allowed",
                "proposal_id": proposal.id,
                "reason": "decision_accepted",
            }

        return {
            "gate": "blocked",
            "proposal_id": proposal.id,
            "reason": "implicit_high_risk_action",
        }

    return None
