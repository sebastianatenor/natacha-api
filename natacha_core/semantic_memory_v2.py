import time
import math
import os
import requests
from google.cloud import firestore

COLLECTION = "semantic_memory_v2"

def _client():
    return firestore.Client()

# === Embeddings con fallback seguro ===
def embed_text(text: str):
    """
    Genera embeddings usando OpenAI si hay API_KEY en entorno.
    Si no, devuelve un vector dummy para no romper nada.
    """
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return [0.0] * 128  # fallback seguro

    try:
        r = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": "text-embedding-3-small",
                "input": text
            },
            timeout=8
        )
        data = r.json()
        return data["data"][0]["embedding"]
    except Exception:
        return [0.0] * 128


def cosine(a, b):
    """
    Similaridad coseno para ranking semántico.
    """
    dp = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dp / (na * nb)


def save_event(user_id: str, project: str, text: str, tags=None, people=None):
    """
    Guarda un evento semántico avanzado (texto + tags + embedding).
    """
    if tags is None:
        tags = []
    if people is None:
        people = []

    emb = embed_text(text)

    doc = {
        "user_id": user_id,
        "project": project,
        "text": text,
        "tags": tags,
        "people": people,
        "embedding": emb,
        "ts": time.time(),
    }

    _client().collection(COLLECTION).add(doc)
    return {"status": "ok", "saved": doc}


def search(query=None, user_id=None, project=None, limit: int = 20):
    """
    Búsqueda semántica real con ranking por similitud.
    Si no hay query -> devuelve últimos eventos.
    """
    docs = (
        _client()
        .collection(COLLECTION)
        .order_by("ts", direction=firestore.Query.DESCENDING)
        .limit(200)
        .stream()
    )

    items = [d.to_dict() for d in docs]

    # Filtros opcionales
    if user_id:
        items = [x for x in items if x.get("user_id") == user_id]
    if project:
        items = [x for x in items if x.get("project") == project]

    # Si no hay query -> devolvemos latest
    if not query:
        return items[:limit]

    # === Ranking semántico ===
    q_emb = embed_text(query)

    for it in items:
        emb = it.get("embedding", [])
        it["score"] = round(cosine(q_emb, emb), 4)

    # ordenamos por score
    items.sort(key=lambda x: x.get("score", 0), reverse=True)

    return {
        "query": query,
        "items": items[:limit]
    }
