"""
Pending Intent — AGENTE_VERAZ

Guarda intenciones bloqueadas a la espera de confirmación explícita.
Memoria VOLÁTIL (proceso).
"""

from typing import Optional, Dict
import threading
from time import time

_LOCK = threading.Lock()
_PENDING: Optional[Dict] = None
TTL_SECONDS = 120  # 2 minutos


def set_pending_intent(signal: Dict):
    global _PENDING
    with _LOCK:
        _PENDING = {
            "signal": signal,
            "timestamp": time(),
        }


def get_pending_intent() -> Optional[Dict]:
    with _LOCK:
        if not _PENDING:
            return None

        if time() - _PENDING["timestamp"] > TTL_SECONDS:
            clear_pending_intent()
            return None

        return _PENDING


def clear_pending_intent():
    global _PENDING
    with _LOCK:
        _PENDING = None
