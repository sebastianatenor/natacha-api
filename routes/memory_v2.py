from fastapi import APIRouter
from typing import List, Optional
import os, json, math, hashlib

from app.memory.schema import MemoryItem, MemoryStoreRequest, MemoryQuery
from utils.dedupe import stable_hash

router = APIRouter(prefix="/memory/v2", tags=["memory-v2"])

DATA_FILE = os.environ.get("MEMORY_FILE", "memory_store.jsonl")

def _is_gcs() -> bool:
    return DATA_FILE.startswith("gs://")

def _gcs_handles():
    from google.cloud import storage
    client = storage.Client()
    bucket_name, blob_name = DATA_FILE.replace("gs://", "", 1).split("/", 1)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return client, bucket, blob

def _gcs_read_all() -> List[dict]:
    _, _, blob = _gcs_handles()
    if not blob.exists():
        return []
    data = blob.download_as_text(encoding="utf-8")
    return [json.loads(line) for line in data.splitlines() if line.strip()]

def _gcs_append_item(item: dict) -> None:
    # Implementación simple: leer todo, agregar y volver a subir
    existing = _gcs_read_all()
    existing.append(item)
    payload = "\n".join(json.dumps(x, ensure_ascii=False) for x in existing)
    _, _, blob = _gcs_handles()
    blob.upload_from_string(payload, content_type="application/jsonl")

def _save(item: dict) -> None:
    if _is_gcs():
        _gcs_append_item(item)
        return
    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

def _load() -> List[dict]:
    if _is_gcs():
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
    # Placeholder determinista
    h = hashlib.md5(text.encode("utf-8")).digest()
    vec = [(b / 255.0) for b in h] * 2   # 32 floats
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
        _save(d)
        added += 1
    return {"status": "ok", "added": added}

@router.post("/search")
def search(q: MemoryQuery):
    data = _load()
    if not data:
        return {"status": "ok", "items": []}

    if q.tags:
        tagset = set(q.tags)
        data = [d for d in data if isinstance(d.get("tags"), list) and tagset.intersection(d["tags"])]

    topk = max(1, min(q.top_k, 50))

    if q.use_semantic:
        qvec = _embed(q.query)
        scored = []
        for d in data:
            sc = _cosine(qvec, d.get("embedding") or _embed(d.get("text","")))
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

# --- mantenimiento: compactar el store (dedup) ---
@router.post("/compact")
def compact_store():
    # cargar todo
    if DATA_FILE.startswith("gs://"):
        items = _gcs_read_all()
    else:
        items = _load_local()

    # dedup por _id (si falta _id, usamos hash del texto)
    seen = {}
    for d in items:
        _id = d.get("_id") or stable_hash(d.get("text",""))
        d["_id"] = _id
        seen[_id] = d  # se queda con la última ocurrencia

    # reescribir
    payload = "\n".join(json.dumps(x, ensure_ascii=False) for x in seen.values())

    if DATA_FILE.startswith("gs://"):
        # subir a GCS
        from google.cloud import storage
        client = storage.Client()
        bucket_name, blob_name = DATA_FILE.replace("gs://","",1).split("/",1)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(payload, content_type="application/jsonl")
    else:
        # escribir local
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            f.write(payload + ("\n" if payload else ""))

    return {"status":"ok","before": len(items), "after": len(seen)}




@router.get("/ops/memory-info")
def memory_info():
    path = DATA_FILE
    try:
        if str(path).startswith("gs://"):
            items = _gcs_read_all()
            backend = "gcs"
        else:
            items = _load_local()
            backend = "local"
        return {"status":"ok","backend":backend,"memory_file":str(path),"count":len(items)}
    except Exception as e:
        return {"status":"error","memory_file":str(path),"error":str(e)}
