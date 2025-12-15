import os

MEMORY_PATH = "/tmp/memory_store.jsonl"
GCS_SOURCE = "gs://natacha-memory-store/memory_store.jsonl"


def memory_state():
    """
    Estado canónico de la memoria de Natacha.
    Fuente de verdad: memory_store.jsonl (una línea = un ítem).
    """

    if not os.path.exists(MEMORY_PATH):
        return {
            "engine": "memory_store",
            "canonical": True,
            "store_loaded": False,
            "items_count": 0,
            "store_path": MEMORY_PATH,
            "source": GCS_SOURCE,
        }

    try:
        with open(MEMORY_PATH, "r") as f:
            count = sum(1 for _ in f)
    except Exception:
        count = None

    return {
        "engine": "memory_store",
        "canonical": True,
        "store_loaded": True,
        "items_count": count,
        "store_path": MEMORY_PATH,
        "source": GCS_SOURCE,
    }
