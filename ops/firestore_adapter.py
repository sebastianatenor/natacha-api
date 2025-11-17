"""
ops.firestore_adapter
----------------------
Conector auxiliar entre el sistema introspectivo y Firestore.
Permite registrar resultados cognitivos y diagnósticos en la base.
"""

from google.cloud import firestore
from datetime import datetime
import os

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "asistente-sebastian")
COLLECTION = "cognitive_logs"

def get_firestore_client():
    """Obtiene el cliente de Firestore autenticado."""
    return firestore.Client(project=PROJECT_ID)


def save_log(entry: dict, kind: str = "generic"):
    """Guarda un registro cognitivo o diagnóstico en Firestore."""
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION).document()
    entry["kind"] = kind
    entry["timestamp"] = datetime.utcnow().isoformat()
    doc_ref.set(entry)
    return {"status": "ok", "id": doc_ref.id}


def list_recent_logs(limit: int = 10):
    """Lista los últimos registros almacenados."""
    db = get_firestore_client()
    docs = db.collection(COLLECTION).order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit).stream()
    return [doc.to_dict() for doc in docs]
