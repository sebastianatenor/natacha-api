
import time
import math
from typing import List, Optional

from google.cloud import firestore
from openai import OpenAI

COLLECTION = "semantic_memory_v2"

_firestore_client = None
_openai_client = None


def _client() -> firestore.Client:
    global _firestore_client
    if _firestore_client is None:
        _firestore_client = firestore.Client()
    return _firestore_client


def _openai_client_instance() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI()
    return _openai_client


def _get_embedding(text: str) -> List[float]:
    """Obtiene un embedding desde OpenAI. Si falla, devuelve []."""
    if not text:
        return []
    try:
        client = _openai_client_instance()
        resp = client.embeddings.create(
            model="text-embedding-3-large",
            input=text,
        )
        return resp.data[0].embedding
    except Exception as e:
        # Podríamos loguear en el futuro; por ahora, fallback silencioso.
        return []


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na ** 0.5 * nb ** 0.5)


def save_event(user_id: str, project: str, text: str, tags=None, people=None):
    """Guarda un evento semántico con embedding en Firestore."""
    if tags is None:
        tags = []
    if people is None:
        people = []

    emb = _get_embedding(text)

    doc = {
        "user_id": user_id,
        "project": project,
        "text": text,
        "tags": tags,
        "people": people,
        "ts": time.time(),
        "embedding": emb,
    }

    _client().collection(COLLECTION).add(doc)
    return {"status": "ok", "saved": doc}


def search(
    user_id: Optional[str] = None,
    project: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 50,
):
    """Búsqueda semántica simple sobre los últimos eventos.

    - Si no hay `q`: devuelve últimos eventos (orden ts desc).
    - Si hay `q`: re-ordena por similitud coseno entre embeddings.
    """
    base = _client().collection(COLLECTION)

    if user_id:
        base = base.where("user_id", "==", user_id)
    if project:
        base = base.where("project", "==", project)

    docs = (
        base.order_by("ts", direction=firestore.Query.DESCENDING)
        .limit(200)
        .stream()
    )

    items = [d.to_dict() for d in docs]

    # Sin query → solo últimos N
    if not q:
        return items[:limit]

    q_emb = _get_embedding(q)
    if not q_emb:
        # Si falló el embedding, devolvemos por fecha
        return items[:limit]

    for item in items:
        emb = item.get("embedding") or []
        item["_score"] = _cosine_similarity(q_emb, emb)

    items.sort(key=lambda x: x.get("_score", 0.0), reverse=True)

    for item in items:
        item.pop("_score", None)

    return items[:limit]
