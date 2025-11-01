from fastapi import APIRouter, HTTPException
from google.cloud import firestore
from google.oauth2 import service_account
from datetime import datetime
import math

router = APIRouter(tags=["semantic"])

def get_db():
    cred_path = "firestore-key.json"
    try:
        creds = service_account.Credentials.from_service_account_file(cred_path)
        return firestore.Client(project="asistente-sebastian", credentials=creds)
    except Exception:
        return firestore.Client(project="asistente-sebastian")

def cosine_similarity(vec1, vec2):
    """Calcula similitud coseno entre dos vectores simples (listas numéricas)."""
    if not vec1 or not vec2:
        return 0
    dot = sum(a*b for a,b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a*a for a in vec1))
    norm2 = math.sqrt(sum(b*b for b in vec2))
    return dot / (norm1 * norm2) if norm1 and norm2 else 0

@router.post("/memory/search_smart")
def search_smart(payload: dict):
    """Busca memorias similares por significado aproximado (versión simple, sin embeddings)."""
    query = payload.get("query", "").lower()
    project = payload.get("project", "general")
    db = get_db()
    docs = db.collection("assistant_memory").where("project", "==", project).stream()
    results = []

    for d in docs:
        data = d.to_dict()
        score = 0
        if query in data.get("summary", "").lower():
            score += 1
        if query in data.get("detail", "").lower():
            score += 1
        results.append({
            "id": d.id,
            "summary": data.get("summary", ""),
            "detail": data.get("detail", ""),
            "score": score,
            "timestamp": data.get("timestamp", "")
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return {"query": query, "matches": results[:10], "found": len(results)}
