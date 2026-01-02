# ops/cognitive/veracity.py
"""
Veracity Guardrail (AGENTE_VERAZ)
Bloquea afirmaciones no verificadas sobre estado del sistema.
Contrato ESTRICTO.
"""

import re
from typing import Dict

FORBIDDEN_PATTERNS = [
    r"\bintent[eé] acceder\b",
    r"\bintent[eé] conectarme\b",
    r"\bprobablemente\b",
    r"\bparece que\b",
    r"\bel sistema est[aá]\b",
    r"\best[aá] operativo\b",
    r"\best[aá] ca[ií]do\b",
    r"\bno est[aá] disponible\b",
    r"\bdeber[ií]a\b",
]

SAFE_FALLBACK = (
    "No tengo verificación directa de ese estado desde el runtime actual. "
    "No puedo afirmarlo con certeza."
)

def check_veracity(answer: str, verified: bool) -> Dict[str, object]:
    """
    Contrato AGENTE_VERAZ

    Retorna SIEMPRE un dict estructurado:
    - allowed: bool
    - verified: bool
    - answer: str
    - reason: str
    """

    if verified:
        return {
            "allowed": True,
            "verified": True,
            "answer": answer,
            "reason": "verified_by_runtime",
        }

    lowered = answer.lower()
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, lowered):
            return {
                "allowed": False,
                "verified": False,
                "answer": SAFE_FALLBACK,
                "reason": "estado no verificado (bloqueado)",
            }

    return {
        "allowed": True,
        "verified": False,
        "answer": answer,
        "reason": "no_verification_but_no_forbidden_claim",
    }
