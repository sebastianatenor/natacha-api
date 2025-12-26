# ops/semantic/gate.py

from typing import Optional, Dict, Any

from ops.semantic.schema import SemanticAnalysis
from ops.semantic.fingerprint import semantic_fingerprint
from ops.semantic.normalize import normalize_semantic_signals

from ops.cognitive.proposals.writer import write_proposal
from ops.cognitive.decisions.resolver import is_fingerprint_accepted

def semantic_gate(
    analysis: SemanticAnalysis,
    source: str = "semantic.analyze",
) -> Optional[Dict[str, Any]]:
    """
    Semantic Gate — B16 FINAL

    - NO ejecuta acciones
    - Detecta acciones implícitas de alto riesgo
    - IDEMPOTENTE (fingerprint)
    - Bloquea por defecto
    - Permite continuar SOLO si existe decisión ACCEPTED
    """

    intent, risk_level = normalize_semantic_signals(analysis)

    # 🔒 Gate solo para acciones implícitas de alto riesgo
    if intent == "implicit_action" and risk_level == "high":

        fingerprint = semantic_fingerprint(analysis)

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
            "confidence": getattr(analysis.signals, "confidence", 0.9),
            "source_revision": "B16",
            "source": source,
            "fingerprint": fingerprint,
        }

        proposal = write_proposal(proposal_data)

        # 🔓 Unlock SOLO con decisión ACCEPTED
        if is_fingerprint_accepted(fingerprint):
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

    # No aplica gate
    return None
