# ops/cognitive/proposals/intelligence.py
from typing import List, Dict, Any
import hashlib


def _hash_key(p: Dict[str, Any]) -> str:
    """
    Stable hash for deduplication.
    Same cause → same hash.
    """
    base = f"{p.get('kind')}|{p.get('source')}|{p.get('title')}"
    return hashlib.sha256(base.encode()).hexdigest()


def score_proposal(p: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assign score, normalized confidence and priority.
    Pure function.
    """
    score = 0

    kind = p.get("kind")
    confidence = float(p.get("confidence", 0.5))

    # --- Heuristics ---
    if kind == "system":
        score += 40
    if kind == "memory":
        score += 25
    if kind == "semantic":
        score += 35

    # confidence influence
    score += int(confidence * 20)

    score = min(score, 100)

    if score >= 70:
        priority = "high"
    elif score >= 40:
        priority = "medium"
    else:
        priority = "low"

    p.update({
        "score": score,
        "priority": priority,
        "confidence": round(confidence, 2),
        "dedup_key": _hash_key(p),
    })

    return p


def enrich_and_dedup(
    proposals: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Score, deduplicate and sort proposals.
    Canonical output.
    """

    bucket = {}

    for p in proposals:
        sp = score_proposal(p)
        key = sp["dedup_key"]

        # keep highest score per key
        if key not in bucket or sp["score"] > bucket[key]["score"]:
            bucket[key] = sp

    # sort by score desc
    ordered = sorted(
        bucket.values(),
        key=lambda x: x.get("score", 0),
        reverse=True,
    )

    return ordered
