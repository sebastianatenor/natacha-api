# v17/semantic/analyzer.py

import hashlib
from v17.contracts import SemanticFrame


def semantic_analyze(text: str) -> SemanticFrame:
    normalized = text.strip().lower()

    intent = "implicit_action" if "automatic" in normalized or "autom" in normalized else "informational"
    risk_level = "high" if intent == "implicit_action" else "low"
    confidence = 0.9 if intent == "implicit_action" else 0.2
    domains = ["automation"] if intent == "implicit_action" else []

    fingerprint = hashlib.sha256(normalized.encode()).hexdigest()

    return SemanticFrame(
        text=text,
        intent=intent,
        risk_level=risk_level,
        confidence=confidence,
        domains=domains,
        fingerprint=fingerprint,
    )
