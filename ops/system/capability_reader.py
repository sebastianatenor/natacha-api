# ops/system/capability_reader.py
import json
from pathlib import Path

MANIFEST_PATH = Path("ops/system/capability_manifest.json")


def read_capability_manifest():
    if not MANIFEST_PATH.exists():
        return {
            "status": "missing",
            "reason": "capability_manifest not found"
        }

    try:
        return {
            "status": "ok",
            "capabilities": json.loads(MANIFEST_PATH.read_text())
        }
    except Exception as e:
        return {
            "status": "error",
            "reason": str(e)
        }
