from flask import Blueprint, request, Response, jsonify
import csv, io, json, datetime, os
from typing import Iterator, Dict, Any, Optional
from google.cloud import storage

memory_export_bp = Blueprint("memory_export_bp", __name__)

# Config (igual que el backend actual)
MEMORY_GCS_URL = os.environ.get("MEMORY_GCS_URL", "gs://natacha-memory-store/memory_store.jsonl")
API_KEY = os.environ.get("API_KEY")

def _auth_ok(req) -> bool:
    key = req.headers.get("X-API-Key")
    return bool(key and API_KEY and key == API_KEY)

def _parse_gs_url(gs_url: str):
    assert gs_url.startswith("gs://"), "URL must start with gs://"
    _, rest = gs_url.split("gs://", 1)
    bucket, blob = rest.split("/", 1)
    return bucket, blob

def _iter_jsonl_from_gcs(gs_url: str) -> Iterator[Dict[str, Any]]:
    bucket_name, blob_name = _parse_gs_url(gs_url)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    if not blob.exists():
        return
    text = blob.download_as_text()
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except Exception:
            continue

def _matches(
    record: Dict[str, Any],
    ns: Optional[str],
    filters: Dict[str, Any],
    since: Optional[datetime.datetime],
    until: Optional[datetime.datetime],
    include_deleted: bool
) -> bool:
    if not include_deleted and record.get("deleted") is True:
        return False
    if ns and record.get("namespace") != ns:
        return False

    item = record.get("item") or {}
    r_type = item.get("type")
    r_tags = item.get("tags") or []
    r_ts   = record.get("ts") or item.get("ts")

    # type
    f_type = (filters or {}).get("type")
    if f_type and r_type != f_type:
        return False

    # tags_any / tags_all / tags_none
    tags_any = (filters or {}).get("tags_any") or []
    if tags_any and not any(t in r_tags for t in tags_any):
        return False

    tags_all = (filters or {}).get("tags_all") or []
    if tags_all and not all(t in r_tags for t in tags_all):
        return False

    tags_none = (filters or {}).get("tags_none") or []
    if tags_none and any(t in r_tags for t in tags_none):
        return False

    # ventana temporal (ISO 8601)
    if since or until:
        try:
            ts = datetime.datetime.fromisoformat(str(r_ts).replace("Z", ""))
        except Exception:
            ts = None
        if since and ts and ts < since:
            return False
        if until and ts and ts > until:
            return False

    return True

def _filter_stream(ns, query_text, filters, limit, since, until, include_deleted) -> Iterator[Dict[str, Any]]:
    count = 0
    for rec in _iter_jsonl_from_gcs(MEMORY_GCS_URL) or []:
        # filtro de texto simple: item.text + item.source
        if query_text:
            it = rec.get("item") or {}
            txt = f"{it.get('text','')} {it.get('source','')}"
            if query_text.lower() not in txt.lower():
                continue

        if _matches(rec, ns, filters or {}, since, until, include_deleted):
            yield rec
            count += 1
            if limit and count >= limit:
                return

@memory_export_bp.route("/memory/v2/export", methods=["POST"])
def memory_export():
    if not _auth_ok(request):
        return jsonify({"error": "unauthorized"}), 401

    body = request.get_json(force=True) or {}
    ns = body.get("namespace")
    query_text = (body.get("query") or "").strip()
    filters = body.get("filters") or {}
    limit = int(body.get("limit") or 0)
    fmt = (body.get("format") or "jsonl").lower()
    include_deleted = bool(body.get("include_deleted") or False)

    def parse_dt(s: Optional[str]):
        if not s: return None
        try:
            return datetime.datetime.fromisoformat(str(s).replace("Z",""))
        except Exception:
            return None

    since = parse_dt(body.get("since"))
    until = parse_dt(body.get("until"))

    if fmt not in ("jsonl", "csv"):
        return jsonify({"error": "format must be jsonl or csv"}), 400

    stream = _filter_stream(ns, query_text, filters, limit, since, until, include_deleted)

    if fmt == "jsonl":
        def gen_jsonl():
            for rec in stream:
                yield json.dumps(rec, ensure_ascii=False) + "\n"
        return Response(gen_jsonl(), mimetype="application/x-ndjson")

    # csv
    def gen_csv():
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["_id","namespace","type","text","tags","source","meta","ts","deleted"])
        yield buf.getvalue(); buf.seek(0); buf.truncate(0)
        for rec in stream:
            item = rec.get("item") or {}
            row = [
                rec.get("_id",""),
                rec.get("namespace",""),
                item.get("type",""),
                (item.get("text") or "").replace("\n"," ").strip(),
                ",".join(item.get("tags") or []),
                item.get("source",""),
                json.dumps(item.get("meta") or {}, ensure_ascii=False),
                rec.get("ts",""),
                rec.get("deleted", False),
            ]
            w.writerow(row)
            yield buf.getvalue(); buf.seek(0); buf.truncate(0)
    return Response(gen_csv(), mimetype="text/csv")

@memory_export_bp.route("/memory/v2/delete", methods=["POST"])
def memory_delete():
    """
    Soft-delete: agrega tombstones (append-only) con deleted:true.
    Body: { "namespace": "...", "ids": ["id1","id2"], "reason": "..." }
    """
    if not _auth_ok(request):
        return jsonify({"error": "unauthorized"}), 401

    body = request.get_json(force=True) or {}
    ns = body.get("namespace")
    ids = body.get("ids") or []
    reason = (body.get("reason") or "").strip()

    if not ns or not ids:
        return jsonify({"error": "namespace and ids are required"}), 400

    bucket_name, blob_name = _parse_gs_url(MEMORY_GCS_URL)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    now = datetime.datetime.utcnow().isoformat() + "Z"
    out_lines = []
    for _id in ids:
        out_lines.append(json.dumps({
            "_id": _id,
            "namespace": ns,
            "ts": now,
            "deleted": True,
            "item": {
                "type": "tombstone",
                "text": f"soft-delete({_id})",
                "source": "ops",
                "tags": ["deleted","tombstone"],
                "meta": {"reason": reason}
            }
        }, ensure_ascii=False))

    current = blob.download_as_text() if blob.exists() else ""
    if current and not current.endswith("\n"):
        current += "\n"
    new_content = current + "\n".join(out_lines) + "\n"
    blob.upload_from_string(new_content, content_type="application/jsonl")

    return jsonify({"status":"ok","deleted_count": len(ids)})
