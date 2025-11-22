import os
import time
import math
from typing import List, Optional, Any, Dict

from google.cloud import firestore
from openai import OpenAI

COLLECTION = "semantic_memory_v2"

_firestore_client = None
_openai_client = None


def _fs() -> firestore.Client:
    """
    Cliente singleton de Firestore.
    """
    global _firestore_client
    if _firestore_client is None:
        _firestore_client = firestore.Client()
    return _firestore_client


def _openai() -> OpenAI:
    """
    Cliente singleton de OpenAI.
    """
    global _openai_client
    if _openai_client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            # Si esto pasa, preferimos explotar explícitamente
            raise RuntimeError("OPENAI_API_KEY no configurada en el entorno")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client


def _embed_text(text: str) -> List[float]:
    """
    Genera un embedding para el texto dado usando un modelo liviano.
    """
    client = _openai()
    # Defensa: por las dudas truncamos textos MUY largos
    if len(text) > 8000:
        text = text[:8000]

    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    # Siempre devolvemos una lista simple de floats
    return list(res.data[0].embedding)


def _cosine(a: List[float], b: List[float]) -> float:
    """
    Similitud coseno defensiva:
    - Si alguna norma es cero -> 0.0
    - Si las longitudes difieren -> se usa el mínimo.
    """
    if not a or not b:
        return 0.0

    n = min(len(a), len(b))
    num = 0.0
    norm_a = 0.0
    norm_b = 0.0

    for i in range(n):
        try:
            x = float(a[i])
            y = float(b[i])
        except (TypeError, ValueError, IndexError):
            # Si algo raro pasa con los tipos, ignoramos ese componente
            continue
        num += x * y
        norm_a += x * x
        norm_b += y * y

    if norm_a <= 0.0 or norm_b <= 0.0:
        return 0.0

    return num / math.sqrt(norm_a * norm_b)


def save_event(user_id: str, project: str, text: str, tags=None, people=None):
    """
    Guarda un evento semántico, con embedding de OpenAI si está disponible.
    """
    if tags is None:
        tags = []
    if people is None:
        people = []

    embedding: List[float] = []
    try:
        embedding = _embed_text(text)
    except Exception as e:
        # Defensa: si algo falla con OpenAI, igual guardamos sin embedding
        print(f"[semantic_memory_v2.save_event] Error generando embedding: {e}")
        embedding = []

    doc = {
        "user_id": user_id,
        "project": project,
        "text": text,
        "tags": tags,
        "people": people,
        "ts": time.time(),
        "embedding": embedding,
    }

    _fs().collection(COLLECTION).add(doc)
    return {"status": "ok", "saved": doc}


def search(limit: int = 50, **filters):
    """
    Búsqueda semántica simple y robusta:
    - Filtra por user_id y project si vienen.
    - Si no hay q -> devuelve últimos eventos por ts (o sin order_by si Firestore se queja).
    - Si hay q -> genera embedding de la query y rankea por similitud coseno.
    - Nunca explota por:
        * índices de Firestore
        * embeddings faltantes o mal formados
        * errores de OpenAI
    """
    user_id: Optional[str] = filters.get("user_id")
    project: Optional[str] = filters.get("project")
    q: Optional[str] = filters.get("q")

    db = _fs()
    base_query = db.collection(COLLECTION)

    if user_id:
        base_query = base_query.where("user_id", "==", user_id)
    if project:
        base_query = base_query.where("project", "==", project)

    # Defensa: aseguramos límite mínimo 1
    limit_value = limit if isinstance(limit, int) and limit > 0 else 50

    # 1) Intento principal: ordenar por ts desc
    try:
        query = (
            base_query
            .order_by("ts", direction=firestore.Query.DESCENDING)
            .limit(limit_value)
        )
        docs = [d.to_dict() for d in query.stream()]
    except Exception as e:
        print(f"[semantic_memory_v2.search] Firestore query con order_by falló: {e}")
        # 2) Fallback: sin order_by, solo limit
        try:
            query = base_query.limit(limit_value)
            docs = [d.to_dict() for d in query.stream()]
        except Exception as e2:
            print(f"[semantic_memory_v2.search] Firestore fallback sin order_by también falló: {e2}")
            # 3) Fallback extremo: nada
            return []

    # Si no hay texto de búsqueda, devolvemos los últimos eventos tal cual
    if not q:
        return docs

    # Intentamos generar embedding de la query; si falla, devolvemos fallback
    try:
        query_vec = _embed_text(q)
    except Exception as e:
        print(f"[semantic_memory_v2.search] Embedding de la query falló: {e}")
        return docs

    results = []
    for d in docs:
        emb = d.get("embedding") or []
        score = 0.0
        if isinstance(emb, list) and emb:
            try:
                score = _cosine(query_vec, emb)
            except Exception as e:
                print(f"[semantic_memory_v2.search] Cálculo de coseno falló: {e}")
                score = 0.0

        d_with_score = dict(d)
        d_with_score["score"] = float(score)
        results.append(d_with_score)

    # Ordenamos por score descendente
    results.sort(key=lambda x: x.get("score", 0.0), reverse=True)

    # Respetamos el límite en la salida
    return results[:limit_value]
