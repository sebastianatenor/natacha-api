# ops/cognitive/proposals/mapper.py
from typing import List, Dict, Any
from datetime import datetime


def proposals_from_signals(
    signals: List[Any],
    source_revision: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Convert signals into cognitive proposals.
    Pure function. No side effects. (B14.2)
    """

    proposals: List[Dict[str, Any]] = []
    ts = datetime.utcnow().isoformat() + "Z"

    for s in signals:
        if s.type == "semantic_inactive":
            proposals.append({
                "kind": "system",
                "title": "Semantic engine inactive",
                "description": "Semantic reasoning is currently disabled.",
                "rationale": "System operates in literal-only mode.",
                "recommendation": "Keep semantic disabled until explicitly enabled.",
                "status": "proposed",
                "confidence": s.confidence,
                "priority": "medium",
                "source": "signal.semantic_inactive",
                "source_revision": source_revision,
                "timestamp": ts,
            })

        if s.type == "memory_growth":
            proposals.append({
                "kind": "memory",
                "title": "Memory store growing",
                "description": "Memory size is increasing beyond baseline.",
                "rationale": "Unbounded growth may impact performance.",
                "recommendation": "Consider snapshot or compaction in future phase.",
                "status": "proposed",
                "confidence": s.confidence,
                "priority": "low",
                "source": "signal.memory_growth",
                "source_revision": source_revision,
                "timestamp": ts,
            })

    return proposals
