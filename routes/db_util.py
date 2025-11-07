from contextlib import contextmanager
from typing import Iterator, Optional

# Opcional: si está disponible Firestore en el entorno, devolvemos un cliente real.
try:
    from google.cloud import firestore  # type: ignore
except Exception:  # lib no disponible o sin credenciales
    firestore = None  # type: ignore

def get_client():
    """
    Retorna un cliente de Firestore si es posible; si no, None.
    Mantiene compatibilidad con rutas que hacen `from routes.db_util import get_client`.
    """
    if firestore is None:
        return None
    try:
        return firestore.Client()
    except Exception:
        return None

@contextmanager
def get_db() -> Iterator[Optional[object]]:
    """
    Stub de contexto DB. Entrega un objeto "cliente" si existe (Firestore), o None.
    Compatible con `from routes.db_util import get_db`.
    """
    yield get_client()
