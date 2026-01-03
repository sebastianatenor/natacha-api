"""
Permission Registry — AGENTE_VERAZ
"""

from typing import Dict

# ⚠️ Stub: luego se puede persistir
_USER_PERMISSIONS: Dict[str, Dict] = {
    "sebastian": {
        "automation": True,
        "filesystem": False,
        "network": False,
    }
}


def has_permission(user_id: str, domain: str) -> bool:
    return bool(
        _USER_PERMISSIONS.get(user_id, {}).get(domain, False)
    )
