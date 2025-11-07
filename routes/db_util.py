from contextlib import contextmanager
from typing import Iterator, Optional

def get_client():
    """
    Return a Firestore client if available, else None.
    """
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
    """
    Context that yields a DB client (or None). Always defined.
    """
    yield get_client()

__all__ = ["get_db", "get_client"]
