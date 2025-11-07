from contextlib import contextmanager
from typing import Iterator, Optional

@contextmanager
def get_db() -> Iterator[Optional[object]]:
    """
    Stub para mantener compatibilidad con 'from routes.db_util import get_db'.
    Devuelve un contexto vacío (None). Reemplazar luego por conexión real si es necesario.
    """
    yield None
