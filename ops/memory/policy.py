"""
Memory Policy Engine
Decide cuándo y qué escribir en memoria canónica.
"""

from datetime import datetime, timezone


IMPORTANT_KINDS = {
    "decision",
    "commitment",
    "state_change",
    "user_preference",
    "milestone",
}


def should_write_memory(event: dict) -> bool:
    """
    Decide si un evento merece persistirse.
    """
    if not isinstance(event, dict):
        return False

    kind = event.get("kind")
    confidence = event.get("confidence", "low")

    if kind in IMPORTANT_KINDS:
        return True

    if confidence == "high":
        return True

    return False


def enrich_event(event: dict) -> dict:
    """
    Normaliza y enriquece eventos antes de persistir.
    """
    event.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    event.setdefault("confidence", "medium")
    return event
