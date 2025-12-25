# ops/cognitive/proposals/scorer.py
from typing import Dict, Any, List


def score_proposal(proposal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assigns score, priority and confidence to a proposal.
    Pure function. No side effects.
    """

    signals = proposal.get("signals", [])
    base_score = 0

    # --- Simple heuristic rules (B13.3) ---
    if "semantic_drift" in signals:
        base_score += 40

    if "memory_inconsistency" in signals:
        base_score += 30

    if "missing_capability" in signals:
        base_score += 20

    if "performance_degradation" in signals:
        base_score += 25

    score = min(base_score, 100)

    if score >= 70:
        priority = "high"
    elif score >= 40:
        priority = "medium"
    else:
        priority = "low"

    confidence = "high" if score >= 60 else "medium"

    proposal.update({
        "score": score,
        "priority": priority,
        "confidence": confidence,
    })

    return proposal


def score_proposals_bulk(
    proposals: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    scored = [score_proposal(p) for p in proposals]

    # Orden descendente por score
    scored.sort(key=lambda x: x.get("score", 0), reverse=True)

    return scored
