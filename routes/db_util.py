from contextlib import contextmanager
from typing import Iterator, Optional

def get_client():
    """Devuelve Firestore Client si está disponible, si no devuelve None."""
    try:
        from google.cloud import firestore  # type: ignore
        return firestore.Client()
    except Exception:
        return None

@contextmanager
def get_db() -> Iterator[Optional[object]]:
    """Context manager compatible: yield del cliente o None."""
    client = get_client()
    try:
        yield client
    finally:
        pass

__all__ = ["get_client", "get_db"]
