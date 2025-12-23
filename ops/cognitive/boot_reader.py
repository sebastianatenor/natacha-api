# ops/cognitive/boot_reader.py

from typing import Optional, Dict, Any
from ops.timeline.reader import read_events


def read_last_cognitive_boot() -> Optional[Dict[str, Any]]:
    """
    Devuelve el último evento `cognitive_boot` persistido.
    No infiere. No razona. Solo lee memoria canónica.
    """
    try:
        events = read_events()
        for ev in reversed(events):
            if ev.get("kind") == "cognitive_boot":
                return ev.get("state")
    except Exception:
        return None

    return None
