from contextlib import contextmanager
from typing import Iterator, Optional

def get_client():
    """Return Firestore client if available, else None."""
    try:
        from google.cloud import firestore  # type: ignore
        try:
            return firestore.Client()
        except Exception:
            return None
    except Exception:
        return None

@contextmanager
def get_db() -> Iterator[Optional[object]]:
    """Yield Firestore client or None (stub)."""
    client = get_client()
    try:
        yield client
    finally:
        pass
