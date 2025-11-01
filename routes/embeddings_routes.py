import os
import math
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from google.cloud import firestore
from google.oauth2 import service_account

router = APIRouter(tags=["embeddings"])

PROJECT_ID = os.getenv("GCP_PROJECT", "asistente-sebastian")

def get_db():
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "firestore-key.json")
    if cred_path and os.path.exists(cred_path):
        creds = service_account.Credentials.from_service_account_file(cred_path)
        return firestore.Client(project=PROJECT_ID, credentials=creds)
    return firestore.Client(project=PROJECT_ID)

def cheap_embed(text: str) -> list[float]:
    """
    Embedding barato determinístico.
    No llama a ningún servicio externo.
    Sirve para comparar entre sí textos que pasen por este mismo método.
    """
    text = (text or "").lower().strip()
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    # 16 números / dims
    dims = []
    for i in range(0, 64, 4):
        chunk = h[i:i+4]
        v = int(chunk, 16) / 0xFFFF  # 0..1
        dims.append(v)
    return dims

def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    if not na or not nb:
        return 0.0
    return dot / (na * nb)

@router.post("/memory/embed")
def memory_embed(payload: dict):
    """
    Guarda una memoria **con vector**.
    payload:
      summary (str) *
      detail (str)
      project (str)
      channel (str)
    """
    summary = payload.get("summary", "")
    detail = payload.get("detail", "")
    project = payload.get("project", "general")
    channel = payload.get("channel", "chatgpt")

    if not summary:
        raise HTTPException(status_code=400, detail="summary is required")

    # armo texto base
    text = summary + " " + detail
    vec = cheap_embed(text)

    db = get_db()
    doc = {
        "summary": summary,
        "detail": detail,
        "project": project,
        "channel": channel,
        "vector": vec,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "state": "vigente",
    }
    db.collection("assistant_memory").add(doc)
    return {"status": "ok", "stored": doc}

@router.post("/memory/search_vector")
def memory_search_vector(payload: dict):
    """
    Busca memorias por similitud de vector.
    payload:
      query (str) *
      project (str)
      limit (int)
    """
    query = payload.get("query", "")
    project = payload.get("project", "general")
    limit = int(payload.get("limit", 10))

    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    qvec = cheap_embed(query)
    db = get_db()

    # traigo solo las de ese proyecto
    docs = db.collection("assistant_memory").where("project", "==", project).stream()
    scored = []
    for d in docs:
        data = d.to_dict()
        vec = data.get("vector")
        if not vec:
            # si no tiene vector, lo ignoro
            continue
        score = cosine(qvec, vec)
        scored.append({
            "id": d.id,
            "summary": data.get("summary", ""),
            "detail": data.get("detail", ""),
            "project": data.get("project", ""),
            "channel": data.get("channel", ""),
            "timestamp": data.get("timestamp", ""),
            "score": score,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return {
        "query": query,
        "project": project,
        "results": scored[:limit],
        "found": len(scored)
    }
