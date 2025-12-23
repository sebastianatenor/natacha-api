# ops/cognitive/boot_writer.py

from datetime import datetime, timezone
import json

from unified_core.memory_paths import get_canonical_memory_path


BOOT_KIND = "cognitive_boot"


def write_cognitive_boot(perception: dict) -> None:
    """
    Persiste el estado perceptivo como punto de arranque cognitivo.
    Escribimos SOLO hechos observables.
    """

    path = get_canonical_memory_path()

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "kind": BOOT_KIND,
        "confidence": "high",
        "perception": perception,
    }

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

