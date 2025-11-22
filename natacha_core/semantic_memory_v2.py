import time
from google.cloud import firestore

COLLECTION = "semantic_memory_v2"

def _client():
    return firestore.Client()

def save_event(user_id: str, project: str, text: str, tags=None, people=None):
    """
    Guarda un evento semántico básico.
    """
    if tags is None:
        tags = []
    if people is None:
        people = []

    doc = {
        "user_id": user_id,
        "project": project,
        "text": text,
        "tags": tags,
        "people": people,
        "ts": time.time(),
    }

    _client().collection(COLLECTION).add(doc)
    return {"status": "ok", "saved": doc}

def search(limit: int = 50):
    """
    Lista últimos eventos semánticos.
    """
    docs = (
        _client()
        .collection(COLLECTION)
        .order_by("ts", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )

    return [d.to_dict() for d in docs]
