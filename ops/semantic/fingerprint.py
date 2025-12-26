# ops/semantic/fingerprint.py

import hashlib
import json
from ops.semantic.schema import SemanticAnalysis


def semantic_fingerprint(analysis: SemanticAnalysis) -> str:
    """
    Genera un fingerprint determinístico para un análisis semántico.

    - Mismo texto + mismas señales → mismo hash
    - Garantiza idempotencia del Semantic Gate (B16)
    """

    payload = {
        "text": analysis.text,
        "intent": analysis.signals.intent,
        "risk_level": analysis.signals.risk_level,
        "domains": analysis.signals.domains,
        "model": analysis.model_used,
    }

    raw = json.dumps(payload, sort_keys=True).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()
