from contextlib import contextmanager
from typing import Iterator, Optional
from datetime import datetime, timezone

# Lazy Firestore import to avoid import-time failures
def _lazy_firestore_client():
    from google.cloud import firestore
    return firestore.Client()

def get_client():
    """Return a Firestore client (uses default creds on Cloud Run)."""
    return _lazy_firestore_client()

@contextmanager
def get_db() -> Iterator[Optional[object]]:
    """
    Minimal stub to satisfy imports.
    If you later wire a real DB (e.g., Firestore wrapper or SQL), replace this.
    """
    # No real DB session; yield None so callers can handle 'no-op' mode.
    yield None

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

__all__ = ["get_client", "get_db", "now_iso"]
