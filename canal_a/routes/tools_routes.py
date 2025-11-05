from fastapi import APIRouter, Response, Query, Request
from typing import List, Optional
from io import StringIO
import csv, json
from google.cloud import firestore

router = APIRouter(prefix="/tools", tags=["tools"])

def _fs():
    return firestore.Client()

@router.get("/export")
def export_notes(owner: str = Query(...), fmt: str = "jsonl", limit: int = 1000):
    fs = _fs()
    docs = (fs.collection("context").document(owner)
               .collection("notes")
               .order_by("ts", direction=firestore.Query.DESCENDING)
               .limit(int(limit)).stream())
    rows = []
    for d in docs:
        data = d.to_dict() or {}
        rows.append({
            "id": d.id,
            "text": data.get("text",""),
            "tags": data.get("tags",[]),
            "ts": (data.get("ts").isoformat() if data.get("ts") else None)
        })
    if fmt.lower() == "csv":
        buf = StringIO()
        w = csv.DictWriter(buf, fieldnames=["id","text","tags","ts"])
        w.writeheader()
        for r in rows:
            w.writerow({
                "id": r["id"],
                "text": r["text"],
                "tags": ",".join(r.get("tags",[])),
                "ts": r["ts"] or ""
            })
        return Response(buf.getvalue(), media_type="text/csv")
    return Response("\n".join(json.dumps(r, ensure_ascii=False) for r in rows),
                    media_type="application/x-ndjson")

from pydantic import BaseModel
class ImportItem(BaseModel):
    text: str
    tags: Optional[List[str]] = None
class ImportPayload(BaseModel):
    items: List[ImportItem]

@router.post("/import")
def import_notes(payload: ImportPayload, owner: str = Query(...), request: Request = None):
    fs = _fs()
    batch = fs.batch()
    coll = fs.collection("context").document(owner).collection("notes")
    count = 0
    for it in payload.items:
        doc_ref = coll.document()
        batch.set(doc_ref, {"text": it.text, "tags": it.tags or [], "ts": firestore.SERVER_TIMESTAMP})
        count += 1
    batch.commit()
    return {"ok": True, "imported": count}
