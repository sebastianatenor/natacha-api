# ops/timeline/utils.py
import os
from pathlib import Path


def get_timeline_path() -> Path:
    """
    Single source of truth for timeline path.
    """
    path = os.getenv("NATACHA_TIMELINE_PATH")

    if not path:
        # fallback ONLY for legacy cloud behavior
        path = "/tmp/timeline.jsonl"

    return Path(path)
