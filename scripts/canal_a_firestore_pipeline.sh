#!/usr/bin/env bash
set -Eeuo pipefail
trap 'code=$?; echo "❌ Pipeline falló en la línea $LINENO (exit $code)"; exit $code' ERR

PROJECT="asistente-sebastian"
REGION="us-central1"
SVC="natacha-api-a"
SA_EMAIL="natacha-firestore-access@${PROJECT}.iam.gserviceaccount.com"

cd ~/natacha-api/canal_a

# 1) requirements
touch requirements.txt
grep -q '^google-cloud-firestore' requirements.txt || echo 'google-cloud-firestore==2.16.0' >> requirements.txt

# 2) ctx_routes con Firestore
cat > routes/ctx_routes.py <<'PY'
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from google.cloud import firestore

router = APIRouter(prefix="/ctx")

def _fs():
    return firestore.Client()

class AddNoteBody(BaseModel):
    text: str
    tags: Optional[List[str]] = None

@router.get("/ping")
def ping():
    return {"ok": True, "ns": "ctx", "firestore": "wired"}

@router.post("/add_note/{owner}")
def add_note(owner: str, body: AddNoteBody):
    ref = _fs().collection("context").document(owner)
    note_doc = {"text": body.text, "tags": body.tags or [], "ts": firestore.SERVER_TIMESTAMP}
    ref.set({"notes": firestore.ArrayUnion([note_doc])}, merge=True)
    return {"ok": True, "appended": True}

@router.get("/{owner}")
def get_ctx(owner: str):
    ref = _fs().collection("context").document(owner)
    snap = ref.get()
    if not snap.exists:
        return {"owner": owner, "notes": []}
    data = snap.to_dict() or {}
    return {"owner": owner, "notes": data.get("notes", [])}
PY

# 3) __init__ para paquete routes (por si acaso)
[ -f routes/__init__.py ] || printf '' > routes/__init__.py

# 4) app_main mínimo del Canal A
cat > app_main.py <<'PY'
from fastapi import FastAPI
from routes import ctx_routes
from routes import ops_routes

app = FastAPI(title="natacha-api-a")
app.include_router(ctx_routes.router)
app.include_router(ops_routes.router)

@app.get("/__alive")
def alive():
    return {"ok": True, "app": "canal-a"}
PY

# 5) ops_routes si no existe
cat > routes/ops_routes.py <<'PY'
from fastapi import APIRouter
from datetime import datetime
router = APIRouter(prefix="/ops")
@router.get("/smart_health")
def smart_health():
    return {"ok": True, "service": "canal-a", "ts": datetime.utcnow().isoformat() + "Z",
            "checks": {"firestore": "skipped", "env": "skipped"}}
PY

# 6) Dockerfile mínimo para Canal A
cat > Dockerfile <<'DOCKER'
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt fastapi uvicorn google-cloud-firestore
COPY . .
ENV PORT=8080
CMD ["uvicorn", "app_main:app", "--host", "0.0.0.0", "--port", "8080"]
DOCKER

# 7) Chequeo sintaxis
python3 -m py_compile routes/ctx_routes.py routes/ops_routes.py app_main.py

# 8) Deploy con SA de Firestore
gcloud run deploy "$SVC" \
  --project "$PROJECT" \
  --region "$REGION" \
  --source . \
  --service-account "$SA_EMAIL" \
  --allow-unauthenticated

# 9) Tests (no fatales si fallan)
SERVICE_URL="$(gcloud run services describe "$SVC" --project "$PROJECT" --region "$REGION" --format='value(status.url)')"
echo "Canal A URL: $SERVICE_URL"

echo "== OpenAPI keys (esperado /ctx/* y /ops/smart_health) =="
curl -s "$SERVICE_URL/openapi.json" | jq -r '.paths | keys[]' | grep -E '^/ctx/|^/ops/|^/__alive' || true

echo "== Pings =="
curl -s "$SERVICE_URL/__alive" | jq || true
curl -s "$SERVICE_URL/ops/smart_health" | jq || true
curl -s "$SERVICE_URL/ctx/ping" | jq || true

echo "== Add note =="
curl -s -X POST "$SERVICE_URL/ctx/add_note/sebastian" -H "Content-Type: application/json" \
  -d '{"text":"first note from Canal A","tags":["canal-a","test"]}' | jq || true

echo "== Read notes =="
curl -s "$SERVICE_URL/ctx/sebastian" | jq || true
