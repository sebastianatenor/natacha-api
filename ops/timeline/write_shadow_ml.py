# ops/timeline/write_shadow_ml.py

from datetime import datetime
from typing import Dict, Any

from ops.timeline.writer import write_event


def write_shadow_ml_event(payload: Dict[str, Any]) -> None:
    """
    Shadow ML logging.
    No afecta decisiones.
    No ejecuta acciones.
    """

    event = {
        "kind": "shadow_ml_sample",
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload,
    }

    write_event(event)
