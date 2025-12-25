# ops/cognitive/proposals/utils.py
import hashlib
import json
from typing import Dict, Any


def compute_proposal_hash(proposal: Dict[str, Any]) -> str:
    """
    Stable hash for deduplication.
    Ignores volatile fields.
    """
    stable_fields = {
        "summary": proposal.get("summary"),
        "source": proposal.get("source"),
        "recommendation": proposal.get("recommendation"),
    }

    raw = json.dumps(stable_fields, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
