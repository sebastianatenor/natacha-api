from contextlib import contextmanager
from typing import Iterator, Optional
from datetime import datetime, timezone

def _lazy_firestore_client():
    # Import perezoso; evita romper import-time si el lib no está
    from google.cloud import firestore  # type: ignore
    return firestore.Client()

def get_client():
    """
    Devuelve un cliente de Firestore.
    En Cloud Run usa el service account del servicio.
    En local podés usar GOOGLE_APPLICATION_CREDENTIALS.
    """
    return _lazy_firestore_client()

@contextmanager
def get_db() -> Iterator[Optional[object]]:
    """
    Context manager homogéneo para usar como 'db' o 'client'.
    """
    client = None
    try:
        client = get_client()
        yield client
    finally:
        # Si algún día agregás cierre/flush, va acá
        pass

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

__all__ = ["get_client", "get_db", "now_iso"]
