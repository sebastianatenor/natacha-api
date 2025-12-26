# ops/semantic/normalize.py
from typing import Tuple, Any


def normalize_semantic_signals(analysis: Any) -> Tuple[str, str]:
    """
    Devuelve (intent, risk_level) de forma tolerante.
    Soporta objetos reales, mocks y dicts.
    """

    signals = getattr(analysis, "signals", None)

    if signals is None:
        return "unknown", "low"

    # Caso objeto fuerte
    intent = getattr(signals, "intent", None)
    risk = getattr(signals, "risk_level", None)

    # Caso dict
    if intent is None and isinstance(signals, dict):
        intent = signals.get("intent")
        risk = signals.get("risk_level")

    return intent or "unknown", risk or "low"
