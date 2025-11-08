from fastapi import APIRouter
from typing import List
import os, json, math, hashlib
from app.memory.schema import MemoryItem, MemoryStoreRequest, MemoryQuery
from utils.dedupe import stable_hash

router = APIRouter(prefix="/memory/v2", tags=["memory-v2"])

DATA_FILE = os.environ.get("MEMORY_FILE", "memory_store.jsonl")

def _save_local(item: dict) -> None:
    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

def _load_local() -> List[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    return dot / (na*nb) if na and nb else 0.0

def _embed(text: str) -> List[float]:
    """
    Placeholder de embeddings deterministas.
    Reemplazá por tu proveedor real cuando quieras.
    """
    h = hashlib.md5(text.encode("utf-8")).digest()
    return [b/255.0 for b in h[:16]]

@router.post("/store")
def store(req: MemoryStoreRequest):
    seen = {}
    added = 0
    for it in req.items:
        key = stable_hash(it.text)
        if key in seen:
            continue
        seen[key] = True
        doc = it.model_dump()
        if doc.get("embedding") is None and os.environ.get("NATACHA_EMBEDDINGS", "on") == "on":
            doc["embedding"] = _embed(it.text)
        doc["_id"] = key
        _save_local(doc)
        added += 1
    return {"status": "ok", "added": added}

@router.post("/search")
def search(q: MemoryQuery):
    data = _load_local()
    if not data:
        return {"status": "ok", "items": []}

    results: List[dict] = []
    use_sem = q.use_semantic and os.environ.get("NATACHA_EMBEDDINGS", "on") == "on"
    qvec = _embed(q.query) if use_sem else None
    qlow = q.query.lower()

    for d in data:
        if q.tags:
            dtags = d.get("tags") or []
            if not set(q.tags).issubset(set(dtags)):
                continue

        score = 0.0
        if use_sem and d.get("embedding"):
            score = _cosine(qvec, d["embedding"])
        if qlow in (d.get("text", "").lower()):
            score += 0.3

        if score > 0.0:
            results.append({
                "_id": d.get("_id"),
                "text": d.get("text"),
                "tags": d.get("tags"),
                "meta": d.get("meta"),
                "score": round(score, 4),
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    topk = max(1, min(q.top_k, 50))
    return {"status": "ok", "items": results[:topk]}
