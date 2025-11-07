from contextlib import contextmanager
from typing import Iterator, Optional

@contextmanager
def get_db() -> Iterator[Optional[object]]:
    """
    Stub: mantiene compatibilidad con rutas que hacen 'from routes.db_util import get_db'.
    Devuelve un contexto vacío. Reemplazar luego por conexión real si hace falta.
    """
    yield None
