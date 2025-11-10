from typing import Optional, Any, Dict
import os
import logging
from datetime import datetime, timezone

# Import perezoso de Firestore para no romper import-time si no está instalado
def _lazy_firestore_client():
    from google.cloud import firestore  # importa sólo cuando se usa
    return firestore.Client()

def get_client():
    """
    Devuelve un cliente de Firestore.
    En Cloud Run usará las credenciales del service account por defecto.
    En local podés usar GOOGLE_APPLICATION_CREDENTIALS si querés.
    """
    return _lazy_firestore_client()

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

__all__ = ["get_client", "now_iso", "get_db"]

# Compat: wrapper esperado por ops_routes
def get_db():
    return get_client()
