"""
B13.2 – Cognitive Proposal Generator
Genera propuestas cognitivas basadas en percepción y drift.
NO ejecuta acciones.
"""

from datetime import datetime
from typing import Optional

from ops.system.perception_provider import read_system_perception
from ops.cognitive.drift_detector import detect_drift
from routes.system_baseline.provider import read_system_baseline
from ops.cognitive.proposals.writer import write_proposal


def generate_proposal_if_needed() -> Optional[dict]:
    baseline = read_system_baseline()
    perception = read_system_perception()

    if not baseline or not perception:
        return None

    drift = detect_drift(baseline, perception)

    if not drift.get("drift_detected"):
        return None

    proposal = {
        "kind": "cognitive_proposal",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "proposal_type": drift.get("recommended_action", "unknown"),
        "severity": drift.get("severity", "low"),
        "rationale": drift.get("reason"),
        "recommended_action": drift.get("recommended_action"),
        "confidence": "medium",
        "source": "B13.2-generator",
    }

    write_proposal(proposal)
    return proposal
