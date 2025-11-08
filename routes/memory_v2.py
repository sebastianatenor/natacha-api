from fastapi import APIRouter
from typing import List, Optional
import os, json, math, hashlib

from app.memory.schema import MemoryItem, MemoryStoreRequest, MemoryQuery
from utils.dedupe import stable_hash

router = APIRouter(prefix="/memory/v2", tags=["memory-v2"])

DATA_FILE = os.environ.get("MEMORY_FILE", "memory_store.jsonl")
USE_GCS = DATA_FILE.startswith("gs://")

if USE_GCS:
    from google.cloud import storage  # requiere google-cloud-storage
    _gcs_client = storage.Client()
    _gcs_bucket, _gcs_blobname = DATA_FILE.replace("gs://", "", 1).split("/", 1)
    _bucket = _gcs_client.bucket(_gcs_bucket)
    _blob = _bucket.blob(_gcs_blobname)

def _gcs_read_all() -> List[dict]:
    if not _blob.exists():
        return []
    data = _blob.download_as_text(encoding="utf-8")
    return [json.loads(line) for line in data.splitlines() if line.strip()]

def _gcs_append_line(line: str) -> None:
    # Append “manual”: descargamos, agregamos y subimos (sencillo y suficiente por ahora)
    existing = _gcs_read_all()
    existing.append(json.loads(line))
    payload = "\n".join(json.dumps(x, ensure_ascii=False) for x in existing)
    _blob.upload_from_string(payload, content_type="application/jsonl")

def _save_local(item: dict) -> None:
    if USE_GCS:
        _gcs_append_line(json.dumps(item, ensure_ascii=False))
        return
    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

def _load_local() -> List[dict]:
    if USE_GCS:
        return _gcs_read_all()
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
    Placeholder determinista. Reemplazar por proveedor real cuando quieras.
    """
    h = hashlib.md5(text.encode("utf-8")).digest()
    # devolvemos 32 floats normalizados (vector fijo)
    vec = [(b / 255.0) for b in h] * 2
    return vec

@router.post("/store")
def store(req: MemoryStoreRequest):
    if not req.items:
        return {"status": "ok", "added": 0}
    added = 0
    for it in req.items:
        d = it.dict()
        d["_id"] = stable_hash(d["text"])
        d["embedding"] = d.get("embedding") or _embed(d["text"])
        _save_local(d)
        added += 1
    return {"status": "ok", "added": added}

@router.post("/search")
def search(q: MemoryQuery):
    data = _load_local()
    if not data:
        return {"status": "ok", "items": []}
    # filtrado por tags si vienen
    if q.tags:
        tagset = set(q.tags)
        data = [d for d in data if d.get("tags") and tagset.intersection(d["tags"])]

    topk = max(1, min(q.top_k, 50))
    # búsqueda semántica (placeholder) o keyword
    if q.use_semantic:
        qvec = _embed(q.query)
        scored = []
        for d in data:
            sc = _cosine(qvec, d.get("embedding") or _embed(d["text"]))
            scored.append((sc, d))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for sc, d in scored[:topk]:
            results.append({
                "_id": d.get("_id"),
                "text": d.get("text"),
                "tags": d.get("tags"),
                "meta": d.get("meta"),
                "score": round(float(sc), 4)
            })
        return {"status": "ok", "items": results}
    else:
        # keyword naive
        ql = q.query.lower()
        ranked = []
        for d in data:
            score = 1.0 if ql in (d.get("text","").lower()) else 0.0
            if score > 0:
                ranked.append((score, d))
        ranked.sort(key=lambda x: x[0], reverse=True)
        results = [{
            "_id": d.get("_id"),
            "text": d.get("text"),
            "tags": d.get("tags"),
            "meta": d.get("meta"),
            "score": round(float(sc), 4)
        } for sc, d in ranked[:topk]]
        return {"status": "ok", "items": results}
