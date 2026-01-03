"""
Permission Gate — AGENTE_VERAZ
"""

from typing import Dict
from ops.cognitive.permission_registry import has_permission


def permission_allowed(user_id: str, signal: Dict) -> bool:
    domains = signal.get("domains", [])
    return all(has_permission(user_id, d) for d in domains)
