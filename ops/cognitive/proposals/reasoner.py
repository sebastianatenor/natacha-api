# ops/cognitive/proposals/reasoner.py
from typing import List, Dict, Any


def generate_proposals(
    perception: Dict[str, Any],
    system_status: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Generate cognitive proposals based on perception + system status.
    READ-ONLY. No side effects. (B13)
    Must conform to CognitiveProposal schema.
    """

    proposals: List[Dict[str, Any]] = []

    semantic = perception.get("semantic", {})
    memory = system_status.get("memory", {})
    revision = system_status.get("runtime", {}).get("revision") or "unknown"

    # --- Proposal: Semantic inactive ---
    if not semantic.get("loaded", False):
        proposals.append({
            "kind": "semantic",
            "title": "Semantic engine inactive",
            "description": "The semantic engine is currently not loaded in runtime.",
            "rationale": (
                "Semantic capabilities are disabled by configuration or startup policy. "
                "This is acceptable in B-phase but should be explicit."
            ),
            "status": "proposed",
            "confidence": 0.7,
            "priority": "medium",
            "signals": ["semantic_drift"],
            "source": "perception.semantic",
            "source_revision": revision,
            "recommendation": "Keep semantic disabled until explicitly enabled by operator.",
        })

    # --- Proposal: Memory size growth ---
    if memory.get("items_count", 0) > 3000:
        proposals.append({
            "kind": "memory",
            "title": "Memory store size is growing",
            "description": "The persistent memory store exceeded 3000 items.",
            "rationale": (
                "Large memory stores may impact recall performance and cognitive clarity "
                "in later phases."
            ),
            "status": "proposed",
            "confidence": 0.6,
            "priority": "low",
            "signals": ["memory_growth"],
            "source": "system.memory",
            "source_revision": revision,
            "recommendation": "Consider snapshotting or compaction in a future B-phase.",
        })

    return proposals
