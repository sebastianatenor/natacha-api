# ops/semantic/fingerprint.py

import hashlib
import json
from ops.semantic.schema import SemanticAnalysis


def semantic_fingerprint(analysis: SemanticAnalysis) -> str:
    """
    B16 CANONICAL fingerprint

    - SIEMPRE retorna fingerprint
    - NO depende de embeddings
    - Determinístico
    - Idempotente
    """

    payload = {
        "intent": getattr(analysis.signals, "intent", ""),
        "risk_level": getattr(analysis.signals, "risk_level", ""),
        "domains": getattr(analysis.signals, "domains", []),
        "confidence": round(getattr(analysis.signals, "confidence", 0), 2),
        "text": analysis.text.strip().lower(),
    }

    raw = json.dumps(payload, sort_keys=True).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()
